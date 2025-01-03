from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import warnings
from app.helpers import parse_custom_date

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="MovedIn20Warning")

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Set log level to WARNING
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Define the base class for ORM models
Base = declarative_base()

# Define the Stock model
class Stock(Base):
    __tablename__ = 'stock_data'
    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(10), nullable=False)
    Date = Column(Date, nullable=False)
    Price = Column(Numeric(12, 2))
    EPS = Column(Numeric(12, 2))
    PER = Column(Numeric(12, 2))

    def __repr__(self):
        return f"<Stock(symbol={self.stock_symbol}, Date={self.date}, Price={self.price}, EPS={self.EPS}, PER={self.PER})>"

# Main script
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Get the database URL
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Replace `postgres://` with `postgresql://` if necessary
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Create database engine
    engine = create_engine(DATABASE_URL, echo=False)  # Disable echo for reduced verbosity

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    # Create a session factory
    Session = sessionmaker(bind=engine)
    session = Session()

    def insert_data_from_csv(file_path, stock_symbol):
        """Insert stock data from a CSV file."""
        try:
            # Read and clean data
            df = pd.read_csv(file_path)
            df['Date'] = df['Date'].apply(parse_custom_date)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            df['EPS'] = pd.to_numeric(df['EPS'], errors='coerce')
            df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

            # Drop rows with missing dates
            df = df.dropna(subset=['Date'])

            # Insert data row by row into the session
            for _, row in df.iterrows():
                stock = Stock(
                    stock_symbol=stock_symbol,
                    Date=row['Date'],
                    Price=row['Price'],
                    EPS=row['EPS'],
                    PER=row['PER']
                )
                session.add(stock)
            session.commit()
            print(f"Data from {file_path} inserted successfully.")
        except Exception as e:
            print(f"Error inserting data from {file_path}: {e}")
            session.rollback()

    # Insert data from CSV files
    insert_data_from_csv('app/data/raw/1104.csv', '1104')

    # Fetch and print a summary of inserted rows
    try:
        count = session.query(Stock).count()
        print(f"Total rows in stock_data: {count}")
    except Exception as e:
        print(f"Error fetching data: {e}")

    # Close the session
    session.close()