from flask import Blueprint, jsonify, request
from app.db.db_CRUD import CRUDHelper
import os
from app.config import INPUT_STOCK_DIR

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create a Blueprint for the API
api = Blueprint('api', __name__)

# Initialize CRUDHelper
crud_helper = CRUDHelper(database_url=DATABASE_URL)


@api.route('/stock', methods=['GET'])
def get_stock_data():
    """Fetch all stock data with pagination."""
    stock_id = request.args.get("stock_id", type=int)
    limit = request.args.get("limit", 100, type=int)
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
            "date": stock.date.isoformat(),
            "price": stock.price,
            "EPS": stock.EPS,
            "PER": stock.PER
        }
        for stock in stocks[offset:offset + limit]
    ]
    return jsonify(result), 200


@api.route('/stock/update', methods=['POST'])
def update_stock_data():
    """Update stock data for a given stock symbol."""
    stock_id = request.args.get("stock_id", type=int)

    if not stock_id:
        return jsonify({"error": "Stock ID is required"}), 400

    crud_helper.update_stock_data(stock_id)

    stocks = crud_helper.get_all_stock_info(stock_id)
    # Serialize the results
    result = [
        {
            "stock_id": stock.stock_id,
            "date": stock.date.isoformat(),
            "Price": stock.price,
            "EPS": stock.EPS,
            "PER": stock.PER
        }
        for stock in stocks
    ]
    return jsonify(result), 200


@api.route('/stock/update_all', methods=['POST'])
def update_all_stock_data():
    """Update stock data for all stock symbols."""

    with open(INPUT_STOCK_DIR / "stock_numbers.txt", "r") as f:
        stock_numbers = f.read().splitlines()

    error_stocks = []
    for stock_id in stock_numbers:
        result = crud_helper.update_stock_data(stock_id)
        print(result)
        if not result:
            error_stocks.append(stock_id)

    if error_stocks:
        return jsonify({"error": f"Failed to update stocks: {error_stocks}"}), 500
    return jsonify({"message": "Stock data updated successfully"}), 200
