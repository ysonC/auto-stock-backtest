from flask import Flask, request, jsonify, render_template
from app import check_and_download_stocks, clean_downloaded_stocks, check_chromedriver, setup_logging, check_all_folders
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from app.backtest import process_stocks  # Import backtesting function
from app.db.models import Stock  # ORM model
from sqlalchemy.orm import scoped_session, sessionmaker

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
def backtest_stock():
    """Fetch stock data for a selected stock and perform backtest."""
    stock_number = request.form.get('stock_number')
    if not stock_number:
        return jsonify({'error': 'Stock number is required'}), 400

    try:
        # Fetch stock data from the database
        session = scoped_session(sessionmaker(bind=db.engine))
        stock_data = session.query(Stock).filter_by(stock_symbol=stock_number).all()
        session.close()

        if not stock_data:
            return jsonify({'error': f'No data found for stock {stock_number}'}), 404

        # Prepare response data
        data = [
            {
                'Date': s.Date.strftime('%Y-%m-%d'),  # Format date without time
                'Price': str(s.Price),
                'EPS': str(s.EPS),
                'PER': str(s.PER)
            }
            for s in stock_data
        ]

        return jsonify({'message': 'Backtest completed successfully!', 'result': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)