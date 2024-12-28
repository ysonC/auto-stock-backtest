import pandas as pd
import os

# Define paths
process_data_path = "data/process_data.xlsx"
stock_folder_path = "data/stock_price"  # Path to the folder containing multiple stock CSV files

# Load process_data.xlsx
process_data_df = pd.read_excel(process_data_path)

# Initialize empty lists for storing results
result_list = []

# Loop through each stock file in the folder
for stock_file in os.listdir(stock_folder_path):
    if stock_file.endswith(".csv"):
        stock_id = stock_file.split(".")[0]  # Extract Stock ID from file name
        stock_file_path = os.path.join(stock_folder_path, stock_file)
        
        # Load the stock CSV
        try:
            stock_data_df = pd.read_csv(stock_file_path)
        except Exception as e:
            print(f"Error reading file {stock_file}: {e}")
            continue

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
        
        # Calculate median reversion win rates
        def calculate_mr_win_rate(data, weeks):
            recent_weeks = data.head(weeks)  # Assume data is sorted by date descending
            median_price = recent_weeks["Price"].median()
            win_rate = (recent_weeks["Price"] - median_price).abs().sum() / len(recent_weeks)
            return win_rate * 100  # Convert to percentage

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
output_file_path = "data/final_processed_data.xlsx"
result_df.to_excel(output_file_path, index=False)

print(f"Final processed data has been saved to {output_file_path}")