from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from app.helpers import parse_custom_date, read_csv

# Define the base class for ORM models
Base = declarative_base()

# Define the Stock model
class Stock(Base):
    __tablename__ = 'stock_data'
    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Numeric(12, 2))
    EPS = Column(Numeric(12, 2))
    PER = Column(Numeric(12, 2))

    def __repr__(self):
        return f"<Stock(symbol={self.stock_symbol}, date={self.date}, price={self.price}, EPS={self.EPS}, PER={self.PER})>"

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
    engine = create_engine(DATABASE_URL, echo=True)

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    # Create a session factory
    Session = sessionmaker(bind=engine)
    session = Session()

    # Function to insert data from a CSV file
    def insert_data_from_csv(file_path, stock_symbol):
        try:
            # Read and clean data
            df = read_csv(file_path)
            df['date'] = df['Date'].apply(parse_custom_date)
            df['price'] = pd.to_numeric(df['Price'], errors='coerce')
            df['EPS'] = pd.to_numeric(df.get('EPS', None), errors='coerce')
            df['PER'] = pd.to_numeric(df.get('PER', None), errors='coerce')

            # Drop rows with missing dates
            df = df.dropna(subset=['date'])

            # Insert data row by row into the session
            for _, row in df.iterrows():
                stock = Stock(
                    stock_symbol=stock_symbol,
                    date=row['date'],
                    price=row['price'],
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
    insert_data_from_csv('app/1101.csv', '1101')
    insert_data_from_csv('app/1102.csv', '1102')
    insert_data_from_csv('app/1103.csv', '1103')

    # Fetch and print sample data
    try:
        stocks = session.query(Stock).limit(10).all()
        for stock in stocks:
            print(stock)
    except Exception as e:
        print(f"Error fetching data: {e}")

    # Close the session
    session.close()