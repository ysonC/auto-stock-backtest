from sqlalchemy import Column, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base

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
        return f"<Stock(symbol={self.stock_symbol}, Date={self.Date}, Price={self.Price}, EPS={self.EPS}, PER={self.PER})>"