from flask import Flask, request, jsonify, render_template
from app import check_and_download_stocks, clean_downloaded_stocks, check_chromedriver, setup_logging, check_all_folders
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from app.backtest import process_stocks  # Import backtesting function
from app.db.db_models import Stock_Prices_Weekly  # ORM model
from sqlalchemy.orm import scoped_session, sessionmaker
from app.api_functions import backtest_stock

app = Flask(__name__)

check_all_folders()
setup_logging(debug_mode=True)
check_chromedriver()

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/backtest', methods=['POST'])
def get_backtest_stock():
    return backtest_stock(db, request.form['stock_number'])


if __name__ == "__main__":
    app.run(debug=True)
