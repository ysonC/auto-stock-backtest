import pandas as pd
import os
from .helpers import *
from .config import PROCESS_DATA_PATH, STOCK_DATA_DIR, OUTPUT_DATA_PATH

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
    
    # Convert PER to numeric and drop NaN values
    data['PER'] = pd.to_numeric(data['PER'], errors='coerce')
    # Drop rows with NaN PER values
    data = data.dropna(subset=['PER'])
    
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

def process_stocks(stock_numbers):
    """
    Process selected stocks for backtesting Median Reversion (MR) success rates.

    Args:
    - stock_numbers (list): List of stock numbers to process.
    """
    
    create_folder(STOCK_DATA_DIR)
    
    # Load process_data.xlsx
    process_data_df = read_csv(PROCESS_DATA_PATH)
    result_list = []

    # Loop through each stock number
    for stock_id in stock_numbers:
        stock_file_path = os.path.join(STOCK_DATA_DIR, f"{stock_id}.csv")
        
        # Check if stock file exists
        if not os.path.exists(stock_file_path):
            print(f"Stock file for {stock_id} not found in {STOCK_DATA_DIR}. Skipping.")
            continue

        # Load the stock CSV
        stock_data_df = read_csv(stock_file_path)
        if stock_data_df is None:
            print(f"Failed to read data for stock {stock_id}. Skipping.")
            continue

        # Reverse data for chronological order
        stock_data_df = stock_data_df.iloc[::-1].reset_index(drop=True)

        # Filter the process_data_df for the current stock
        stock_row = process_data_df[process_data_df["Stock ID"].astype(str) == stock_id]
        if stock_row.empty:
            print(f"No matching stock ID for {stock_id} in process_data.csv. Skipping.")
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
    save_to_csv(result_df, OUTPUT_DATA_PATH, False)
    return result_df

if __name__ == "__main__":
    stock_numbers = ["1213", "2330", "2303"]  # Example stock numbers
    process_stocks(stock_numbers)
