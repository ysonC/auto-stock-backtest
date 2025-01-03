from flask import Flask, request, jsonify, render_template
from sqlalchemy.orm import scoped_session, sessionmaker
from app.db.db_models import Stock_Prices_Weekly  # ORM model
from dotenv import load_dotenv
import os
from app.db.db_CRUD import CRUDHelper
from app.logging_config import setup_logging

# Configure logging
setup_logging(debug_mode=True)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Use the singleton instance
crud_helper = CRUDHelper(DATABASE_URL)

# Update stock data for a specific stock symbol
result = crud_helper.update_stock_data("1102")
# result = crud_helper.get_latest_stock_info("1101")
print(result)

# Reuse the same instance elsewhere
same_crud_helper = CRUDHelper()
print(crud_helper is same_crud_helper)  # True

# Close the helper when done
crud_helper.close()
