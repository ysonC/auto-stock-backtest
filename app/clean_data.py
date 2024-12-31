import pandas as pd
from pathlib import Path
import os
from .helpers import *
from .config import DATA_DIR, STOCK_DATA_DIR, DOWNLOAD_DIR, PROCESS_DATA_PATH, RESULTS_DIR


def clean_downloaded_stocks(stock_numbers):
    # Input and output directories
    create_folder(DATA_DIR)
    create_folder(STOCK_DATA_DIR)
    create_folder(RESULTS_DIR)

    # Initialize an empty list to collect all summaries
    all_summaries = []

    # Loop through all CSV files in the `download` directory
    for stock_id in stock_numbers:
        filename = f"{stock_id}.csv"
        file_path = os.path.join(DOWNLOAD_DIR, filename)

        if not os.path.exists(file_path):
            print(f"File {filename} does not exist in the download directory.")
            continue
    # Load CSV file into a DataFrame
        df = read_csv(file_path)

        # Ensure column names match expectations
        expected_columns = ['Date', 'Price', 'Change', '% Change',
                            'EPS', 'PER', '8X', '9.8X', '11.6X', '13.4X', '15.2X', '17X']
        if not all(col in df.columns for col in expected_columns):
            print(
                f"File {filename} is missing some expected columns: {expected_columns}")
            continue  # Skip this file

        # Extract Date and Price columns and save to a separate file for each stock
        if 'Date' in df.columns and 'Price' in df.columns:
            date_price_df = df[['Date', 'Price', 'PER']].dropna(
                subset=['Date', 'Price', 'PER'])
            output_file = STOCK_DATA_DIR / f"{stock_id}.csv"
            save_to_csv(date_price_df, output_file, False)
            # date_price_df.to_csv(output_file, index=False)
            # print(f"Date and Price data for {stock_id} saved to {output_file}")

        # Calculate required values
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

        # Assuming the first row contains the latest data
        latest_row = df.iloc[0]
        latest_per = latest_row['PER']
        latest_closing_price = latest_row['Price']

        # Drop rows with NaN in 'PER' for further calculations
        df_clean = df.dropna(subset=['PER'])

        # Calculate statistical metrics
        mean_per = df_clean['PER'].mean() if not df_clean.empty else None
        min_per = df_clean['PER'].min() if not df_clean.empty else None
        median_per = df_clean['PER'].median() if not df_clean.empty else None
        max_per = df_clean['PER'].max() if not df_clean.empty else None
        quartile_per = df_clean['PER'].quantile(
            0.25) if not df_clean.empty else None

        quartile_delta = (latest_per - quartile_per) / (max_per -
                                                        min_per) if latest_per and quartile_per and max_per and min_per else None
        median_delta = (latest_per - median_per) / (max_per -
                                                    min_per) if latest_per and median_per and max_per and min_per else None
        mean_delta = (latest_per - mean_per) / (max_per -
                                                min_per) if latest_per and mean_per and max_per and min_per else None
        min_delta = (latest_per - min_per) / (max_per -
                                              min_per) if latest_per and min_per and max_per and min_per else None

        median_price = (median_per / latest_per) * \
            latest_closing_price if median_per and latest_per and latest_closing_price else None

        # Summary for this stock
        summary = {
            "Stock ID": stock_id,
            "Price": latest_closing_price,
            "Current PER": latest_per,
            "GEP.25": round(quartile_per, 2),
            "GEP MED": round(median_per, 2),
            "Min PER": round(min_per, 2),
            "Max PER": round(max_per, 2),
            "5Y Mean": round(mean_per, 2),
            "25 Delta": round(quartile_delta, 2),
            "Median Delta": round(median_delta, 2),
            "Mean Delta": round(mean_delta, 2),
            "Min Delta": round(min_delta, 2)
        }

        # Append the summary to the list
        all_summaries.append(summary)

    # Convert all summaries to a DataFrame
    summary_df = pd.DataFrame(all_summaries)
    # print(summary_df)

    # Save the combined summary to a CSV file
    save_to_csv(summary_df, PROCESS_DATA_PATH, False)
    return summary_df


if __name__ == "__main__":
    clean_downloaded_stocks()
