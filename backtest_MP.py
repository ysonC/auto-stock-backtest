import pandas as pd
import os
from helpers import*
"""
Column W (1M MR)
Step 1: Find the median (中位數)from column F. After finding the median, 
identify every instance of PER that is below the median. For example median PER was 16, 
find every week data with PER below 16. After that, for every instance, go up 4 rows, 
which is about 1 month. If the value got closer to 16, closer to the median, it counts as success. 
We do that for 1 Month (4 Rows), 2 Months (8 rows), and 3 Months (12 rows) in terms of calculating the success rate. 
If 5 out of the 10 incidents for 1 month time, 1M MR is 50%. We then do that for 2 months and 3 months also.
"""

# Calculate median reversion win rates
def calculate_mr_win_rate(data, weeks):
    total_under_median = 0
    total_improve_median = 0
    for i in range(len(data) - weeks):  # Ensure there's enough data for 'week' lookahead
        enter_PER = data["PER"].iloc[i]
        if enter_PER > median_per:
            continue
        total_under_median += 1
        exit_PER = data["PER"].iloc[i + weeks]
        if exit_PER < median_per and exit_PER > enter_PER:
            total_improve_median += 1
            #print(f"Row {i}: Enter PER = {enter_PER}, Exit PER = {exit_PER}")
    success_rate = total_improve_median/total_under_median*100
    #print(f"Success rate = {success_rate}")
    return success_rate
    

# Define paths
process_data_path = "data/process_data.xlsx"
stock_folder_path = "data/stock_price"  # Path to the folder containing multiple stock CSV files

# Load process_data.xlsx
process_data_df = read_excel(process_data_path)

# Initialize empty lists for storing results
result_list = []

# Loop through each stock file in the folder
for stock_file in os.listdir(stock_folder_path):
    if stock_file.endswith(".csv"):
        stock_id = stock_file.split(".")[0]
        stock_file_path = os.path.join(stock_folder_path, stock_file)
        
        # Load the stock CSV
        stock_data_df = read_csv(stock_file_path)
        
        # Reverse data for chronological order
        stock_data_df = stock_data_df.iloc[::-1].reset_index(drop=True)

        # Filter the process_data_df for the current stock
        stock_row = process_data_df[process_data_df["Stock ID"] == stock_file]
        if stock_row.empty:
            print(f"No matching stock ID for {stock_file} in process_data.xlsx.")
            continue
        
        # Extract necessary values
        current_price = stock_row["Price"].iloc[0]
        current_per = stock_row["Current PER"].iloc[0]
        median_per = stock_row["GEP MED"].iloc[0]

        # Compute requested columns
        median_price = (median_per / current_per) * current_price if current_per != 0 else None
        mp_updown = (median_price - current_price) / current_price if current_price != 0 else None

        mr_1m = calculate_mr_win_rate(stock_data_df, 4)
        mr_2m = calculate_mr_win_rate(stock_data_df, 8)
        mr_3m = calculate_mr_win_rate(stock_data_df, 12)
        avg_mr = pd.Series([mr_1m, mr_2m, mr_3m]).mean()

        # Append the results to the list
        result_list.append({
            "Stock ID": stock_id,
            "C$": current_price,
            "M$": median_price,
            "T$": None,  # Leave blank
            "MP UpDown": mp_updown,
            "1M MR": mr_1m,
            "2M MR": mr_2m,
            "3M MR": mr_3m,
            "Avg.": avg_mr
        })

# Convert results to DataFrame
result_df = pd.DataFrame(result_list)
print(result_df)
# Save the final result to a new Excel file
output_file_path = "data/backtest_MP_data.xlsx"
result_df.to_excel(output_file_path, index=False)

print(f"Backtested data has been saved to {output_file_path}")