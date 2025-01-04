from flask import Blueprint, jsonify, request
from app.db.db_CRUD import CRUDHelper
import os

# Configure database
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create a Blueprint for the API
api = Blueprint('api', __name__)

# Initialize CRUDHelper
crud_helper = CRUDHelper(database_url=DATABASE_URL)

@api.route('/stocks/<int:stock_id>', methods=['GET'])
def get_stock(stock_id):
    """Fetch the latest stock information."""
    stock = crud_helper.get_latest_stock_info(stock_id)
    if not stock:
        return jsonify({"error": "Stock not found"}), 404
    return jsonify({
        "stock_id": stock.stock_id,
        "Date": stock.Date.isoformat(),
        "Price": stock.Price,
        "EPS": stock.EPS,
        "PER": stock.PER
    })

@api.route('/stocks', methods=['GET'])
def get_stocks():
    """Fetch all stock data with pagination."""
    stock_id = request.args.get("stock_id", type=int)
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)

    if not stock_id:
        return jsonify({"error": "Stock ID is required"}), 400

    stocks = crud_helper.get_all_stock_info(stock_id)
    if not stocks:
        return jsonify({"error": "No stocks found"}), 404

    # Serialize the results
    result = [
        {
            "stock_id": stock.stock_id,
            "Date": stock.Date.isoformat(),
            "Price": stock.Price,
            "EPS": stock.EPS,
            "PER": stock.PER
        }
        for stock in stocks[offset:offset + limit]
    ]
    return jsonify(result)

