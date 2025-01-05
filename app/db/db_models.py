from sqlalchemy import Column, Integer, String, Date, Numeric, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

# Define the base class for ORM models
Base = declarative_base()

# Define the Stock model


    # id = Column(Integer, primary_key=True)
class Stock_Prices_Weekly(Base):
    __tablename__ = 'stock_prices_weekly'
    stock_id = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Numeric(12, 2))
    EPS = Column(Numeric(12, 2))
    PER = Column(Numeric(12, 2))
    __table_args__ = (
        PrimaryKeyConstraint('stock_id', 'date'),
    )
    def __repr__(self):
        return f"<Stock(id={self.stock_id}, Date={self.date}, Price={self.price}, EPS={self.EPS}, PER={self.PER})>"
