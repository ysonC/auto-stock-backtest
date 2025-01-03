from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
# Import CRUDHelper for database operations
from app.db.db_CRUD import CRUDHelper
from app.db.db_models import Stock_Prices_Weekly  # ORM model
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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
    return render_template('index.html')

# @app.route('/backtest', methods=['POST'])
# def get_backtest_stock():
#     return backtest_stock(db, request.form['stock_number'])


@app.route('/stocks', methods=['GET'])
def get_all_stock_info():
    stock_symbol = request.args.get('stock_symbol')  # Retrieve query parameter
    if not stock_symbol:
        return render_template('index.html', error="Stock symbol is required.")

    try:
        stock_data = crud_helper.get_all_stock_info(stock_symbol)
        if not stock_data:
            return render_template(
                'index.html',
                error=f"No data found for stock symbol: {stock_symbol}",
            )

        return render_template(
            'index.html',
            stock_data=stock_data,
            stock_symbol=stock_symbol,
        )
    except Exception as e:
        return render_template(
            'index.html',
            error=f"An error occurred: {str(e)}",
        )


if __name__ == "__main__":
    app.run(debug=True)
