import os
import logging
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from app.db.db_CRUD import CRUDHelper
from flask_sqlalchemy import SQLAlchemy
from app.logging_config import setup_logging

app = Flask(__name__)

setup_logging(debug_mode=True)
# Load environment variables
load_dotenv()

# Configure database
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize CRUDHelper with the database URL
crud_helper = CRUDHelper(DATABASE_URL)


@app.route('/')
def index():
    logging.info("Rendering index page")
    return render_template('index.html')

# @app.route('/backtest', methods=['POST'])
# def get_backtest_stock():
#     return backtest_stock(db, request.form['stock_number'])


@app.route('/stocks', methods=['GET'])
def get_all_stock_info():
    stock_id = request.args.get('stock_id')  # Retrieve query parameter
    if not stock_id:
        return render_template('index.html', error="Stock symbol is required.")

    try:
        # Attempt to fetch stock data
        stock_data = crud_helper.get_all_stock_info(stock_id)
        print(stock_data)
        # If no data is found, try downloading it
        if not stock_data:
            download_result = crud_helper.update_stock_data(stock_id)
            if download_result:
                stock_data = crud_helper.get_all_stock_info(stock_id)

        # Handle scenarios where data could not be retrieved
        if not stock_data:
            return render_template(
                'index.html',
                error=f"No data available for stock symbol: {stock_id}",
            )

        # Render template with stock data
        return render_template(
            'index.html',
            stock_data=stock_data,
            stock_id=stock_id,
        )

    except Exception as e:
        logging.error(f"Error fetching stock data for symbol {stock_id}: {e}")
        return render_template(
            'index.html',
            error="An error occurred while processing your request. Please try again later.",
        )

if __name__ == "__main__":
    app.run(debug=True)
