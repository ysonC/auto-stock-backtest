import pandas as pd
import os
from .helpers import *

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input_stock"
DOWNLOAD_DIR = BASE_DIR / "download"
DATA_DIR = BASE_DIR / "data"
STOCK_PRICE_DIR = DATA_DIR / "stock_price"

def backtest_MR(data, weeks, median_per):
    """
    Perform a backtest for Median Reversion (MR) success rates.

    Args:
    - data (DataFrame): Stock data containing the PER column.
    - weeks (int): Number of rows to look ahead.
    - median_per (float): The median PER value.

    Returns:
    - success_rate (float): Success rate as a percentage.
    """
    total_under_median = 0
    total_improve_median = 0

    for i in range(len(data) - weeks):
        enter_PER = data["PER"].iloc[i]
        if enter_PER > median_per:
            continue
        total_under_median += 1
        exit_PER = data["PER"].iloc[i + weeks]
        if exit_PER < median_per and exit_PER > enter_PER:
            total_improve_median += 1

    success_rate = (total_improve_median / total_under_median * 100) if total_under_median > 0 else 0
    return success_rate


def process_stocks():
    """
    Process all stocks for backtesting Median Reversion (MR) success rates.

    Args:
    - process_data_path (str): Path to the process_data Excel file.
    - stock_folder_path (str): Path to the folder containing stock CSV files.
    - output_file_path (str): Path to save the final backtested data.
    """
    # Define path
    create_folder(STOCK_PRICE_DIR)
    process_data_path = "data/process_data.csv"
    output_file_path = "data/backtest_MR_data.csv"
    
    # Load process_data.xlsx
    process_data_df = read_csv(process_data_path)
    result_list = []

    # Loop through each stock file in the folder
    for stock_file in os.listdir(STOCK_PRICE_DIR):
        if stock_file.endswith(".csv"):
            stock_id = stock_file.split(".")[0]
            stock_file_path = os.path.join(STOCK_PRICE_DIR, stock_file)

            # Load the stock CSV
            stock_data_df = read_csv(stock_file_path)
            if stock_data_df is None:
                continue

            # Reverse data for chronological order
            stock_data_df = stock_data_df.iloc[::-1].reset_index(drop=True)

            # Filter the process_data_df for the current stock
            stock_row = process_data_df[process_data_df["Stock ID"].astype(str) == stock_id]
            if stock_row.empty:
                print(f"No matching stock ID for {stock_file} in process_data.csv.")
                continue

            # Extract necessary values
            current_price = stock_row["Price"].iloc[0]
            current_per = stock_row["Current PER"].iloc[0]
            median_per = stock_row["GEP MED"].iloc[0]

            # Compute requested columns
            median_price = (median_per / current_per) * current_price if current_per != 0 else None
            mp_updown = (median_price - current_price) / current_price if current_price != 0 else None

            # Perform Median Reversion backtests
            mr_1m = backtest_MR(stock_data_df, 4, median_per)
            mr_2m = backtest_MR(stock_data_df, 8, median_per)
            mr_3m = backtest_MR(stock_data_df, 12, median_per)
            avg_mr = pd.Series([mr_1m, mr_2m, mr_3m]).mean()

            # Append the results to the list
            result_list.append({
                "Stock ID": stock_id,
                "C$": current_price,
                "M$": median_price,
                "T$": "####",  # Leave blank
                "MP UpDown": mp_updown,
                "1M MR": mr_1m,
                "2M MR": mr_2m,
                "3M MR": mr_3m,
                "Avg.": avg_mr
            })

    # Convert results to DataFrame and save
    result_df = pd.DataFrame(result_list)
    save_to_csv(result_df, output_file_path, False)
    print("###########################################################################################")
    print(result_df)
    print("###########################################################################################")


if __name__ == "__main__":
    process_stocks()