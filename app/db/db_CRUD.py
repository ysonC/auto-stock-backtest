import pandas as pd
import logging
import warnings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
from app.db.db_models import Stock_Prices_Weekly
from app.helpers import parse_custom_date
from app.download_stocks import download_stock_data
from datetime import datetime, timedelta
from app.config import DOWNLOAD_DIR
from app.helpers import read_csv

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="MovedIn20Warning")

# Configure logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class CRUDHelper:
    _instance = None  # Class-level attribute for singleton instance

    def __new__(cls, database_url=None):
        if cls._instance is None:
            cls._instance = super(CRUDHelper, cls).__new__(cls)
            cls._instance._init(database_url)
        return cls._instance

    def _init(self, database_url):
        """Initialize the database connection if not already done."""
        if hasattr(self, "engine"):
            return  # Prevent reinitialization
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql://", 1)
        self.engine = create_engine(database_url, echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_latest_stock_info(self, stock_id):
        """Fetch the latest stock information for a given stock symbol."""
        logging.info(f"Fetching latest stock info for {stock_id}")
        try:
            return (
                self.session.query(Stock_Prices_Weekly)
                .filter_by(stock_id=stock_id)
                .order_by(desc(Stock_Prices_Weekly.Date))
                .first()
            )
        except Exception as e:
            logging.error(f"Error fetching latest stock info: {e}")
            return None
        finally:
            self.session.close()

    def get_all_stock_info(self, stock_id):
        """Fetch all stock information for a given stock symbol."""
        logging.info(f"Fetching all stock info for {stock_id}")
        try:
            return (
                self.session.query(Stock_Prices_Weekly)
                .filter_by(stock_id=stock_id)
                .order_by(desc(Stock_Prices_Weekly.date))
                .all()
            )
        except Exception as e:
            logging.error(f"Error fetching all stock info: {e}")
            return None
        finally:
            self.session.close()

    def update_stock_data(self, stock_id):
        """Check and update 
        tock data for a given stock symbol."""
        try:
            # Fetch the latest stock info
            latest_stock = self.get_latest_stock_info(stock_id)
            
            # If no data exists, download everything
            if not latest_stock:
                logging.info(
                    f"No data for stock {stock_id}, downloading all data.")
                error_stocks = download_stock_data([stock_id])
                if stock_id in error_stocks:
                    logging.error(
                        f"Stock {stock_id} not found. Download failed.")
                    return False
                
                # Read and parse the downloaded data
                df = read_csv(DOWNLOAD_DIR / f"{stock_id}.csv")
                df['Date'] = df['Date'].apply(parse_custom_date)
                df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
                df['EPS'] = pd.to_numeric(df['EPS'], errors='coerce')
                df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

                # Insert new rows into the database
                for _, row in df.iterrows():
                    stock = Stock_Prices_Weekly(
                        stock_id=stock_id,
                        date=row['Date'],
                        price=row['Price'],
                        EPS=row['EPS'],
                        PER=row['PER']
                    )
                    self.session.add(stock)
                self.session.commit()
                return True
            
            # Check if the data is up-to-date with the most recent weekday
            today = datetime.now().date()
            if today.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                most_recent_weekday = today - timedelta(days=today.weekday() - 4)
            else:
                most_recent_weekday = today

            # Compare the latest stock date with the most recent weekday
            logging.info(f"Comparing latest_stock.Date: {latest_stock.date} with most_recent_weekday: {most_recent_weekday}")
            if latest_stock.date == most_recent_weekday:
                logging.info(f"Stock {stock_id} data is up-to-date. No update required.")
                return True
            
            # Download the latest data
            download_stock_data([stock_id])
            downloaded_file_path = f"app/data/raw/{stock_id}.csv"

            # Read and parse the downloaded data
            df = pd.read_csv(downloaded_file_path)
            df['Date'] = df['Date'].apply(parse_custom_date)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            df['EPS'] = pd.to_numeric(df['EPS'], errors='coerce')
            df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

            # Filter data to include only new entries
            df = df[df['Date'] > latest_stock.Date]
            if df.empty:
                logging.info(f"No new data for stock {stock_id}.")
                return True

            # Insert new rows into the database
            for _, row in df.iterrows():
                stock = Stock_Prices_Weekly(
                    stock_id=stock_id,
                    date=row['Date'],
                    price=row['Price'],
                    EPS=row['EPS'],
                    PER=row['PER']
                )
                self.session.add(stock)
            self.session.commit()
            logging.info(f"Stock {stock_id} updated successfully.")
            return True
        except Exception as e:
            logging.error(f"Error updating stock {stock_id}: {e}")
            self.session.rollback()
            return False
        
        finally:
            self.session.close()
 
    def close(self):
        """Close the session."""
        self.session.close()
