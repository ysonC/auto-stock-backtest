from sqlalchemy import Column, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base

# Define the base class for ORM models
Base = declarative_base()

# Define the Stock model


class Stock_Prices_Weekly(Base):
    __tablename__ = 'stock_prices_weekly'
    id = Column(Integer, primary_key=True)
    stock_id = Column(Numeric(12, 2), nullable=False)
    Date = Column(Date, nullable=False)
    Price = Column(Numeric(12, 2))
    EPS = Column(Numeric(12, 2))
    PER = Column(Numeric(12, 2))

    def __repr__(self):
        return f"<Stock(symbol={self.stock_id}, Date={self.Date}, Price={self.Price}, EPS={self.EPS}, PER={self.PER})>"
