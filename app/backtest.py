import pandas as pd
import os
import logging
from .helpers import *
from .config import PROCESS_DATA_PATH, STOCK_DATA_DIR, OUTPUT_DATA_PATH


NaN_THRESHOLD = 0.2


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
        return float('nan'), float('nan')

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
    """
    Process selected stocks for backtesting Median Reversion (MR) success rates.

    Args:
    - stock_numbers (list): List of stock numbers to process.
    """
    logging.info(f"Processing stocks: {stock_numbers}")

    create_folder(STOCK_DATA_DIR)

    # Load process_data.csv
    process_data_df = read_csv(PROCESS_DATA_PATH)
    if process_data_df is None:
        logging.error("Failed to read process_data.csv. Exiting.")
        return

    result_list = []

    # Loop through each stock number
    for stock_id in stock_numbers:
        logging.info(f"Processing stock: {stock_id}")
        stock_file_path = os.path.join(STOCK_DATA_DIR, f"{stock_id}.csv")

        # Check if stock file exists
        if not os.path.exists(stock_file_path):
            logging.warning(
                f"Stock file for {stock_id} not found in {STOCK_DATA_DIR}. Skipping.")
            continue

        # Load the stock CSV
        stock_data_df = read_csv(stock_file_path)
        if stock_data_df is None:
            logging.error(
                f"Failed to read data for stock {stock_id}. Skipping.")
            continue

        # Reverse data for chronological order
        stock_data_df = stock_data_df.iloc[::-1].reset_index(drop=True)

        # Filter the process_data_df for the current stock
        stock_row = process_data_df[process_data_df["Stock ID"].astype(
            str) == stock_id]
        if stock_row.empty:
            logging.warning(
                f"No matching stock ID for {stock_id} in process_data.csv. Skipping.")
            continue

        # S => Z information
        median_per = stock_row["GEP MED"].iloc[0]
        current_per = stock_row["Current PER"].iloc[0]
        quartile_per = stock_row["GEP.25"].iloc[0]

        # S T V
        current_price = stock_row["Price"].iloc[0]
        median_price = (median_per / current_per) * \
            current_price if current_per != 0 else None
        mp_updown = (median_price - current_price) / \
            current_price if current_price != 0 else None

        # Perform Median Reversion backtests
        # W X Y Z
        MR_1_month, MR_cases_1_month = median_reversion_calculation(
            stock_data_df, 4, median_per, quartile_per)
        MR_2_month, MR_cases_2_month = median_reversion_calculation(
            stock_data_df, 8, median_per, quartile_per)
        MR_3_month, MR_cases_3_month = median_reversion_calculation(
            stock_data_df, 12, median_per, quartile_per)
        avg_mr = pd.Series([MR_1_month, MR_2_month, MR_3_month]).mean()

        # AB => AG
        kelly = (avg_mr * (mp_updown + 1) - 1) / \
            mp_updown if mp_updown != 0 else None
        verdict = False
        if mp_updown > 0 and avg_mr > 0.84:
            verdict = True

        # Append the results to the list
        result_list.append({
            "Stock ID": stock_id,
            "C$": current_price,
            "M$": median_price,
            "T$": "####",  # Leave blank
            "MP UpDown": mp_updown,
            "1M MR": MR_1_month,
            "2M MR": MR_2_month,
            "3M MR": MR_3_month,
            "Avg.": avg_mr,
            "####": "####",  # Leave blank
            "Kelly": kelly,
            "Verdict": verdict,
            "#####": "#####",  # Leave blank
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
