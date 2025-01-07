from decimal import Decimal
import pandas as pd
import os
import logging
from .helpers import *
from .config import PROCESS_DATA_PATH, STOCK_DATA_DIR, OUTPUT_DATA_PATH
from app.db.db_CRUD import CRUDHelper
from app.logging import setup_logging

setup_logging(debug_mode=True)

NaN_THRESHOLD = 0.2

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# Initialize CRUDHelper
crud_helper = CRUDHelper(database_url=DATABASE_URL)


def median_reversion_calculation(data, weeks, median_per, quartile_per):
    """
    Perform a backtest for Median Reversion (MR) success rates.

    Args:
    - data (DataFrame): Stock data containing the PER column.
    - weeks (int): Number of rows to look ahead.
    - median_per (float): The median PER value.
    - quartile_per (float): The 25th percentile PER value.

    Returns:
    - success_rate (float): Success rate as a percentage.
    - total_improve_median (int): Total number of successful median improvements.
    """

    logging.info(
        f"Starting backtest for {weeks} weeks with median PER: {median_per}")

    total_under_median = 0
    total_improve_median = 0

    # Convert PER to numeric
    data['PER'] = pd.to_numeric(data['PER'], errors='coerce')
    total_NaN = 0
    total_NaN = data['PER'].isna().sum()

    # Check if NaN values exceed the threshold
    if total_NaN / len(data) > NaN_THRESHOLD:
        logging.warning(
            f"NaN values exceed the threshold of {NaN_THRESHOLD * 100}%. Returning NaN.")
        return float('nan')

    for i in range(len(data) - weeks):
        enter_PER = data["PER"].iloc[i]
        if enter_PER > quartile_per:
            continue
        total_under_median += 1
        initial_deviation = abs(enter_PER - median_per)

        for j in range(1, weeks + 1):
            future_per = data["PER"].iloc[i + j]
            future_deviation = abs(future_per - median_per)
            if future_deviation < initial_deviation:
                total_improve_median += 1
                break

    success_rate = (total_improve_median /
                    total_under_median) if total_under_median > 0 else 0
    logging.info(f"Backtest completed. Success rate: {success_rate:.2f}%")
    return success_rate, total_improve_median


def process_stocks(stock_numbers):
    logging.info(f"Processing stocks: {stock_numbers}")

    result_list = []

    for stock_id in stock_numbers:
        logging.info(f"Processing stock: {stock_id}")

        # Fetch 5 years of stock data from the database
        stocks = crud_helper.get_5_years_stock_info(stock_id)
        if not stocks:
            logging.warning(f"No data found for stock {stock_id}. Skipping.")
            continue

        # Convert the fetched data to a DataFrame
        stock_data_df = pd.DataFrame([{
            "Date": stock.date,
            "Price": float(stock.price) if isinstance(stock.price, Decimal) else stock.price,
            "EPS": float(stock.EPS) if isinstance(stock.EPS, Decimal) else stock.EPS,
            "PER": float(stock.PER) if isinstance(stock.PER, Decimal) else stock.PER
        } for stock in stocks])

        # Ensure the data is sorted chronologically
        stock_data_df = stock_data_df.sort_values(
            by="Date").reset_index(drop=True)

        # Calculate required statistics
        median_per = stock_data_df["PER"].median()  # Median PER
        quartile_per = stock_data_df["PER"].quantile(
            0.25)  # 25th percentile PER
        current_per = stock_data_df["PER"].iloc[-1]  # Most recent PER
        current_price = stock_data_df["Price"].iloc[-1]  # Most recent price
        median_price = (median_per / current_per) * \
            current_price if current_per != 0 else None
        mp_updown = (median_price - current_price) / \
            current_price if current_price != 0 else None

        # Perform Median Reversion backtests
        MR_1_month, MR_cases_1_month = median_reversion_calculation(
            stock_data_df, 4, median_per, quartile_per)
        MR_2_month, MR_cases_2_month = median_reversion_calculation(
            stock_data_df, 8, median_per, quartile_per)
        MR_3_month, MR_cases_3_month = median_reversion_calculation(
            stock_data_df, 12, median_per, quartile_per)
        avg_mr = pd.Series([MR_1_month, MR_2_month, MR_3_month]).mean()

        # Calculate Kelly Criterion and verdict
        kelly = (avg_mr * (mp_updown + 1) - 1) / \
            mp_updown if mp_updown != 0 else None
        verdict = False
        if mp_updown > 0 and avg_mr > 0.84:
            verdict = True

        # Append the results to the list
        result_list.append({
            "Stock ID": stock_id,
            "C$": round(current_price, 2) if current_price is not None else None,
            "M$": round(median_price, 2) if median_price is not None else None,
            "T$": "####",  # Leave blank
            "MP UpDown": round(mp_updown, 2) if mp_updown is not None else None,
            "1M MR": round(MR_1_month, 2) if MR_1_month is not None else None,
            "2M MR": round(MR_2_month, 2) if MR_2_month is not None else None,
            "3M MR": round(MR_3_month, 2) if MR_3_month is not None else None,
            "Avg.": round(avg_mr, 2) if avg_mr is not None else None,
            "Kelly": round(kelly, 2) if kelly is not None else None,
            "Verdict": verdict,
            "1M Incident": MR_cases_1_month,
            "2M Incident": MR_cases_2_month,
            "3M Incident": MR_cases_3_month
        })
        logging.info(f"Processing for stock {stock_id} completed.")

    # Convert results to DataFrame and save
    result_df = pd.DataFrame(result_list)
    save_to_csv(result_df, OUTPUT_DATA_PATH, False)
    logging.info(f"Results saved to {OUTPUT_DATA_PATH}.")
    return result_df


if __name__ == "__main__":
    logging.info("Script execution started.")
    stock_numbers = ["1213", "2330", "2303"]  # Example stock numbers
    try:
        process_stocks(stock_numbers)
    except Exception as e:
        logging.critical(
            f"Unhandled exception during processing: {e}", exc_info=True)
    logging.info("Script execution finished.")
