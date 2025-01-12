from flask import Blueprint, jsonify, request, Response, json
from app.db.db_CRUD import CRUDHelper
import os
from app.config import INPUT_STOCK_DIR, RESOURCES_DIR
from app.backtest_dev import process_stocks
from app.download_stocks import download_stock_data
import pandas as pd

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
        return Response('{"error": "Stock ID is required"}', status=400, mimetype='application/json')

    stocks = crud_helper.get_all_stock_info(stock_id)
    if not stocks:
        return Response('{"error": "No stocks found"}', status=404, mimetype='application/json')

    # Serialize the results
    result_df = pd.DataFrame([{
        "stock_id": stock.stock_id,
        "date": stock.date.isoformat(),
        "price": stock.price,
        "EPS": stock.EPS,
        "PER": stock.PER
    } for stock in stocks[offset:offset + limit]])

    result_json = result_df.to_json(orient='records')
    return Response(result_json, status=200, mimetype='application/json')


@api.route('/stock/5years', methods=['GET'])
def get_stock_data_5years():
    """Fetch 5 years of stock data."""
    stock_id = request.args.get("stock_id", type=int)

    if not stock_id:
        return Response('{"error": "Stock ID is required"}', status=400, mimetype='application/json')

    stocks = crud_helper.get_5_years_stock_info(stock_id)
    if not stocks:
        return Response('{"error": "No stocks found"}', status=404, mimetype='application/json')

    # Serialize the results
    result_df = pd.DataFrame([{
        "stock_id": stock.stock_id,
        "date": stock.date.isoformat(),
        "price": stock.price,
        "EPS": stock.EPS,
        "PER": stock.PER
    } for stock in stocks])

    result_json = result_df.to_json(orient='records')
    return Response(result_json, status=200, mimetype='application/json')


@api.route('/stock/update', methods=['POST'])
def update_stock_data():
    """Update stock data for a given stock symbol."""
    stock_id = request.args.get("stock_id", type=int)

    if not stock_id:
        return Response('{"error": "Stock ID is required"}', status=400, mimetype='application/json')

    crud_helper.update_stock_data(stock_id)

    stocks = crud_helper.get_all_stock_info(stock_id)
    result_df = pd.DataFrame([{
        "stock_id": stock.stock_id,
        "date": stock.date.isoformat(),
        "Price": stock.price,
        "EPS": stock.EPS,
        "PER": stock.PER
    } for stock in stocks])

    result_json = result_df.to_json(orient='records')
    return Response(result_json, status=200, mimetype='application/json')


@api.route('/stock/update_all', methods=['POST'])
def update_all_stock_data():
    """Update stock data for all stock symbols."""
    with open(RESOURCES_DIR / "all_stocks_number.txt", "r") as f:
        stock_numbers = f.read().splitlines()

    # Download all stock data first
    download_stock_data(stock_numbers)

    all_missing_records = []  # Collect all missing records
    updated_stocks = []       # Stocks that need to be updated
    already_updated_stocks = []  # Stocks that are already up-to-date
    error_stocks = []         # Stocks that encountered errors

    for stock_id in stock_numbers:
        try:
            missing_records = crud_helper.update_stock_data(stock_id)
            if missing_records:
                all_missing_records.extend(missing_records)
                updated_stocks.append(stock_id)
            else:
                already_updated_stocks.append(stock_id)
        except Exception as e:
            error_stocks.append(stock_id)

    # Insert all missing records into the database at once
    if all_missing_records:
        success = crud_helper.add_bulk_stock_data(all_missing_records)
        if not success:
            return Response(
                '{"error": "Failed to insert missing records into the database."}',
                status=500,
                mimetype='application/json'
            )

    # Return categorized results
    result = {
        "updated": updated_stocks,
        "already_updated": already_updated_stocks,
        "errors": error_stocks
    }

    # Use json.dumps with separators to format JSON as a single line per array
    response_json = json.dumps(result, separators=(',', ':'))
    return Response(
        response=response_json,
        status=200,
        mimetype='application/json'
    )

@api.route('/stock/backtest', methods=['POST'])
def perform_backtest():
    """Perform backtesting for Median Reversion strategy."""
    stock_numbers = request.json.get("stock_numbers", [])

    try:
        stock_numbers = list(map(int, stock_numbers))
    except ValueError:
        return Response('{"error": "Stock numbers must be integers"}', status=400, mimetype='application/json')

    try:
        result_df = process_stocks(stock_numbers)

        if result_df is not None:
            result_json = result_df.to_json(orient='records')
            return Response(result_json, status=200, mimetype='application/json')
        else:
            return Response('{"error": "No results generated"}', status=500, mimetype='application/json')
    except Exception as e:
        return Response(f'{{"error": "{str(e)}"}}', status=500, mimetype='application/json')


@api.route('/upload', methods=['POST'])
def upload_excel_data():
    try:
        data = request.get_json()
        if not data:
            return Response('{"status": "error", "message": "No data provided"}', status=400, mimetype='application/json')

        tickers = [item['Ticker'] for item in data]
        print("Tickers received:", tickers)

        try:
            result_df = process_stocks(tickers)

            result_json = result_df.to_json(orient='records')
            print("Result JSON:", result_json)
            return Response(result_json, status=200, mimetype='application/json')
        except Exception as e:
            return Response(f'{{"status": "error", "message": "Processing error: {str(e)}"}}', status=500, mimetype='application/json')

    except Exception as e:
        return Response(f'{{"status": "error", "message": "Invalid request: {str(e)}"}}', status=500, mimetype='application/json')
