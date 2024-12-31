import pandas as pd
from pathlib import Path
import os
import logging
from .helpers import *
from .config import DATA_DIR, STOCK_DATA_DIR, DOWNLOAD_DIR, PROCESS_DATA_PATH, RESULTS_DIR


def clean_downloaded_stocks(stock_numbers):
    """
    Cleans and processes downloaded stock data, calculates statistics, and generates a summary.

    Args:
    - stock_numbers (list): List of stock IDs to process.

    Returns:
    - summary_df (DataFrame): DataFrame containing the summary of processed stocks.
    """
    logging.info("Starting clean_downloaded_stocks function.")

    # Ensure required directories exist
    create_folder(DATA_DIR)
    create_folder(STOCK_DATA_DIR)
    create_folder(RESULTS_DIR)
    logging.info("Verified required folders: DATA_DIR, STOCK_DATA_DIR, RESULTS_DIR.")

    # Initialize an empty list to collect all summaries
    all_summaries = []

    # Process each stock in the list
    for stock_id in stock_numbers:
        logging.info(f"Processing stock: {stock_id}")

        # Define the file path
        filename = f"{stock_id}.csv"
        file_path = os.path.join(DOWNLOAD_DIR, filename)

        # Check if the file exists
        if not os.path.exists(file_path):
            logging.warning(f"File {filename} does not exist in the download directory. Skipping.")
            continue

        # Load the CSV file
        df = read_csv(file_path)
        if df is None:
            logging.error(f"Failed to read {filename}. Skipping.")
            continue

        # Check for expected columns
        expected_columns = ['Date', 'Price', 'Change', '% Change',
                            'EPS', 'PER', '8X', '9.8X', '11.6X', '13.4X', '15.2X', '17X']
        if not all(col in df.columns for col in expected_columns):
            logging.warning(f"File {filename} is missing expected columns. Skipping.")
            continue

        # Extract and save Date, Price, and PER columns
        if 'Date' in df.columns and 'Price' in df.columns and 'PER' in df.columns:
            date_price_df = df[['Date', 'Price', 'PER']]
            output_file = Path(STOCK_DATA_DIR) / f"{stock_id}.csv"
            save_to_csv(date_price_df, output_file, False)
            logging.info(f"Extracted and saved Date, Price, PER for {stock_id} to {output_file}.")
        else:
            logging.warning(f"Missing Date, Price, or PER columns in {filename}. Skipping.")
            continue

        # Ensure numeric conversion
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

        # Handle empty or invalid DataFrame
        if df.empty:
            logging.warning(f"DataFrame for {stock_id} is empty after cleaning. Skipping.")
            continue

        # Calculate required metrics
        latest_row = df.iloc[0]
        latest_per = latest_row['PER']
        latest_closing_price = latest_row['Price']

        df_clean = df.dropna(subset=['PER'])

        mean_per = df_clean['PER'].mean() if not df_clean.empty else None
        min_per = df_clean['PER'].min() if not df_clean.empty else None
        median_per = df_clean['PER'].median() if not df_clean.empty else None
        max_per = df_clean['PER'].max() if not df_clean.empty else None
        quartile_per = df_clean['PER'].quantile(0.25) if not df_clean.empty else None

        quartile_delta = (latest_per - quartile_per) / (max_per - min_per) if all([latest_per, quartile_per, max_per, min_per]) else None
        median_delta = (latest_per - median_per) / (max_per - min_per) if all([latest_per, median_per, max_per, min_per]) else None
        mean_delta = (latest_per - mean_per) / (max_per - min_per) if all([latest_per, mean_per, max_per, min_per]) else None
        min_delta = (latest_per - min_per) / (max_per - min_per) if all([latest_per, min_per, max_per, min_per]) else None

        # Create a summary for this stock
        summary = {
            "Stock ID": stock_id,
            "Price": latest_closing_price,
            "Current PER": latest_per,
            "GEP.25": round(quartile_per, 2) if quartile_per else None,
            "GEP MED": round(median_per, 2) if median_per else None,
            "Min PER": round(min_per, 2) if min_per else None,
            "Max PER": round(max_per, 2) if max_per else None,
            "5Y Mean": round(mean_per, 2) if mean_per else None,
            "25 Delta": round(quartile_delta, 2) if quartile_delta else None,
            "Median Delta": round(median_delta, 2) if median_delta else None,
            "Mean Delta": round(mean_delta, 2) if mean_delta else None,
            "Min Delta": round(min_delta, 2) if min_delta else None
        }
        all_summaries.append(summary)
        logging.info(f"Summary for {stock_id}: {summary}.")

    # Combine all summaries into a single DataFrame
    summary_df = pd.DataFrame(all_summaries)

    # Save the summary DataFrame
    save_to_csv(summary_df, PROCESS_DATA_PATH, False)
    logging.info(f"Combined summary saved to {PROCESS_DATA_PATH}.")

    return summary_df


if __name__ == "__main__":
    logging.info("Script execution started.")
    try:
        stock_numbers = ["2303", "2330"]  # Example stock IDs
        clean_downloaded_stocks(stock_numbers)
    except Exception as e:
        logging.critical(f"Unhandled exception in clean_downloaded_stocks: {e}", exc_info=True)
    logging.info("Script execution finished.")
