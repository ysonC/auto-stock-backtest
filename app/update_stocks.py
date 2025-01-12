import os
import logging
from app.db.db_CRUD import CRUDHelper
from app.config import RESOURCES_DIR
from app.app_logging import setup_logging
from app.download_stocks import download_stock_data, check_and_download_stocks

# Setup logging
setup_logging(debug_mode=True)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Initialize CRUDHelper
crud_helper = CRUDHelper(database_url=DATABASE_URL)


def update_all_stock_data():
    """Update stock data for all stock symbols."""
    logging.info("Loading stock numbers from file...")
    try:
        with open(RESOURCES_DIR / "all_stocks_number.txt", "r") as f:
            stock_numbers = f.read().splitlines()
        logging.info(f"Loaded {len(stock_numbers)} stock numbers.")
    except Exception as e:
        logging.error(f"Error loading stock numbers: {e}")
        raise

    # Step 1: Download all stock data locally first
    logging.info("Checking and downloading missing stock data...")
    try:
        error_download = check_and_download_stocks(stock_numbers)
        if error_download:
            logging.warning(f"Failed to download data for stocks: {error_download}")
    except Exception as e:
        logging.error(f"Error during stock download process: {e}")
        raise

    # Step 2: Initialize tracking lists
    all_missing_records = []  # Collect all missing records
    updated_stocks = []       # Stocks that need to be updated
    already_updated_stocks = []  # Stocks that are already up-to-date
    error_stocks = []         # Stocks that encountered errors

    # Step 3: Update the database
    logging.info("Starting database updates...")
    for stock_id in stock_numbers:
        try:
            missing_records = crud_helper.update_stock_data(stock_id)
            if missing_records:
                all_missing_records.extend(missing_records)
                updated_stocks.append(stock_id)
                logging.info(f"Stock {stock_id} updated with missing records.")
            else:
                already_updated_stocks.append(stock_id)
                logging.info(f"Stock {stock_id} is already up-to-date.")
        except Exception as e:
            error_stocks.append(stock_id)
            logging.error(f"Error updating stock {stock_id}: {e}")

    # Step 4: Insert missing records into the database at once
    if all_missing_records:
        logging.info(f"Inserting {len(all_missing_records)} missing records into the database...")
        try:
            success = crud_helper.add_bulk_stock_data(all_missing_records)
            if not success:
                logging.error("Failed to insert missing records into the database.")
                return False
        except Exception as e:
            logging.error(f"Error during bulk insert: {e}")
            raise

    # Step 5: Return categorized results
    result = {
        "updated": updated_stocks,
        "already_updated": already_updated_stocks,
        "errors": error_stocks
    }
    logging.info(f"Update process completed. Results: {result}")
    return result


if __name__ == "__main__":
    logging.info("Script execution started.")
    try:
        update_results = update_all_stock_data()
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True)
    logging.info("Script execution finished.")
