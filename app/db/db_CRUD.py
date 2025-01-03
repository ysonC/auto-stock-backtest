from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
from app.db.db_models import Stock_Prices_Weekly
from app.helpers import parse_custom_date
from app.download_stocks import download_stock_data
import pandas as pd
import logging
import warnings
from datetime import datetime
from app.config import DOWNLOAD_DIR

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

    def get_latest_stock_info(self, stock_symbol):
        """Fetch the latest stock information for a given stock symbol."""
        logging.info(f"Fetching latest stock info for {stock_symbol}")
        try:
            return (
                self.session.query(Stock_Prices_Weekly)
                .filter_by(stock_symbol=stock_symbol)
                .order_by(desc(Stock_Prices_Weekly.Date))
                .first()
            )
        except Exception as e:
            logging.error(f"Error fetching latest stock info: {e}")
            return None

    def get_all_stock_info(self, stock_symbol):
        """Fetch all stock information for a given stock symbol."""
        logging.info(f"Fetching all stock info for {stock_symbol}")
        try:
            return (
                self.session.query(Stock_Prices_Weekly)
                .filter_by(stock_symbol=stock_symbol)
                .order_by(Stock_Prices_Weekly.Date)
                .all()
            )
        except Exception as e:
            logging.error(f"Error fetching all stock info: {e}")
            return None

    def update_stock_data(self, stock_symbol):
        """Check and update stock data for a given stock symbol."""
        try:
            # Fetch the latest stock info
            latest_stock = self.get_latest_stock_info(stock_symbol)

            # If no data exists, download everything
            if not latest_stock:
                logging.info(
                    f"No data for stock {stock_symbol}, downloading all data.")
                download_stock_data([stock_symbol])
                # Read and parse the downloaded data
                df = pd.read_csv(DOWNLOAD_DIR / f"{stock_symbol}.csv")
                df['Date'] = df['Date'].apply(parse_custom_date)
                df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
                df['EPS'] = pd.to_numeric(df['EPS'], errors='coerce')
                df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

                # Insert new rows into the database
                for _, row in df.iterrows():
                    stock = Stock_Prices_Weekly(
                        stock_symbol=stock_symbol,
                        Date=row['Date'],
                        Price=row['Price'],
                        EPS=row['EPS'],
                        PER=row['PER']
                    )
                    self.session.add(stock)
                self.session.commit()
                return "Stock not found. Downloaded and update to database."
            
            # Check if the data is up-to-date
            if latest_stock.Date == datetime.now().date():
                logging.info(
                    f"Stock {stock_symbol} data is up-to-date. No update required.")
                return "No updates required."
            
            # Download the latest data
            download_stock_data([stock_symbol])
            downloaded_file_path = f"app/data/raw/{stock_symbol}.csv"

            # Read and parse the downloaded data
            df = pd.read_csv(downloaded_file_path)
            df['Date'] = df['Date'].apply(parse_custom_date)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            df['EPS'] = pd.to_numeric(df['EPS'], errors='coerce')
            df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

            # Filter data to include only new entries
            df = df[df['Date'] > latest_stock.Date]
            print(df)
            if df.empty:
                logging.info(f"No new data for stock {stock_symbol}.")
                return "No updates required."

            # Insert new rows into the database
            for _, row in df.iterrows():
                stock = Stock_Prices_Weekly(
                    stock_symbol=stock_symbol,
                    Date=row['Date'],
                    Price=row['Price'],
                    EPS=row['EPS'],
                    PER=row['PER']
                )
                self.session.add(stock)
            self.session.commit()
            logging.info(f"Stock {stock_symbol} updated successfully.")
            return "Update completed."
        except Exception as e:
            logging.error(f"Error updating stock {stock_symbol}: {e}")
            self.session.rollback()
            return "Update failed."

    def close(self):
        """Close the session."""
        self.session.close()
