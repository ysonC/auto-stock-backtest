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
                .order_by(desc(Stock_Prices_Weekly.date))
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

    def get_5_years_stock_info(self, stock_id):
        """Fetch 5 years of stock information for a given stock symbol."""
        logging.info(f"Fetching 5 years of stock info for {stock_id}")
        try:
            return (
                self.session.query(Stock_Prices_Weekly)
                .filter_by(stock_id=stock_id)
                .order_by(desc(Stock_Prices_Weekly.date))
                .limit(260)
                .all()
            )
        except Exception as e:
            logging.error(f"Error fetching 5 years of stock info: {e}")
            return None
        finally:
            self.session.close()

    def update_stock_data(self, stock_id):
        """Prepare missing stock data for insertion."""
        stock_file_path = DOWNLOAD_DIR / f"{stock_id}.csv"

        # Check if the stock file exists
        if not stock_file_path.exists():
            logging.error(f"Stock file {stock_file_path} not found. Please ensure data is downloaded.")
            return []

        try:
            # Fetch the latest stock info
            latest_stock = self.get_latest_stock_info(stock_id)

            # Read and parse the downloaded data
            df = read_csv(stock_file_path)
            df['Date'] = df['Date'].apply(parse_custom_date)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            df['EPS'] = pd.to_numeric(df['EPS'], errors='coerce')
            df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

            # If no data exists in the database, return all rows as missing
            if not latest_stock:
                logging.info(f"No data for stock {stock_id} in the database. Preparing all rows for insertion.")
            else:
                # Filter data to include only new entries
                df = df[df['Date'] > latest_stock.date]
                if df.empty:
                    logging.info(f"No new data for stock {stock_id}. Data is already up-to-date.")
                    return []

            # Create and return a list of Stock_Prices_Weekly objects
            stock_records = [
                Stock_Prices_Weekly(
                    stock_id=stock_id,
                    date=row['Date'],
                    price=row['Price'],
                    EPS=row['EPS'],
                    PER=row['PER']
                )
                for _, row in df.iterrows()
            ]

            logging.info(f"Prepared {len(stock_records)} new records for stock {stock_id}.")
            return stock_records
        except Exception as e:
            logging.error(f"Error preparing stock {stock_id}: {e}")
            return []

            
    def add_bulk_stock_data(self, stock_records):
        """Insert multiple stock records into the database in bulk."""
        try:
            self.session.bulk_save_objects(stock_records)
            self.session.commit()
            logging.info(f"Inserted {len(stock_records)} records into the database successfully.")
            return True
        except Exception as e:
            logging.error(f"Error inserting bulk stock data: {e}")
            self.session.rollback()
            return False
        finally:
            self.session.close()

    def close(self):
        """Close the session."""
        self.session.close()
