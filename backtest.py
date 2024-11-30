import os
import pandas as pd

# Directories
data_dir = "data"
stock_data_dir = os.path.join(data_dir, "stock")
output_file = os.path.join(data_dir, "backtest_results.xlsx")
process_data_file = os.path.join(data_dir, "process_data.xlsx")

# Load the processed data
df_processed = pd.read_excel(process_data_file)

# Initialize results list
backtest_results = []

def load_stock_file(file_path):
    """Loads stock data from the given file path."""
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def calculate_exit_results(df_stock, i, closing_price, months):
    """Calculate exit strategy details."""
    exit_index = i + months * 4  # Each month ~4 weeks
    if exit_index < len(df_stock):
        exit_price = df_stock.loc[exit_index, "Closing Price"]
        exit_date = df_stock.loc[exit_index, "Date"]
        profit = exit_price - closing_price
        if profit > 0:
            success = True
        else:
            success = False
        return {
            "Exit Date": exit_date,
            "Exit Price": exit_price,
            "Profit": profit,
            "Successful Trade": success
        }
    return {
        "Exit Date": None,
        "Exit Price": None,
        "Profit": None,
        "Successful Trade": None
    }

# Process each stock file
for filename in os.listdir(stock_data_dir):
    if not filename.endswith("_price.xlsx"):
        continue

    stock_id = filename.split("_")[0]  # Extract stock ID from filename
    file_path = os.path.join(stock_data_dir, filename)

    # Match "Good Entry" PE for this stock
    stock_data = df_processed[df_processed["Stock ID"].astype(str) == stock_id]
    if stock_data.empty:
        print(f"No matching data for Stock ID {stock_id}, skipping.")
        continue

    good_entry = stock_data["Good Entry"].values[0]
    df_stock = load_stock_file(file_path)
    if df_stock is None:
        continue

    # Reverse data for chronological order
    df_stock = df_stock.iloc[::-1].reset_index(drop=True)

    # Perform the backtest
    purchase_details = []
    invalid_purchase = 0
    for i, row in df_stock.iterrows():
        if row["PER"] >= good_entry:
            continue
        
        
        closing_price = row["Closing Price"]
        entry_date = row["Date"]
        results_for_entry = {
            "Stock ID": stock_id,
            "Entry Date": entry_date,
            "Entry Price": closing_price
        }

        for months, label in [(3, "3 Months"), (6, "6 Months"), (12, "1 Year")]:
            exit_results = calculate_exit_results(df_stock, i, closing_price, months)
            results_for_entry.update({
                f"{label} Exit Date": exit_results["Exit Date"],
                f"{label} Exit Price": exit_results["Exit Price"],
                f"{label} Profit": exit_results["Profit"],
                f"{label} Successful Trade": exit_results["Successful Trade"]
            })
            # if(label == "1 Year"):
            #     print(label)
            #     print(entry_date)
            #     print(exit_results["Successful Trade"]) 
            if exit_results["Successful Trade"] is None:
                invalid_purchase += 1

        purchase_details.append(results_for_entry)

    if not purchase_details:
        continue

    # Summarize results for this stock
    total_trades = len(purchase_details)
    success_rates = {}
    for label in ["3 Months", "6 Months", "1 Year"]:
        valid_trades = sum(1 for d in purchase_details if d[f"{label} Successful Trade"] is not None)
        successful_trades = sum(1 for d in purchase_details if d[f"{label} Successful Trade"] is True)
        if valid_trades > 0:
            success_rate = (successful_trades / valid_trades) * 100
        else:
            success_rate = None  # or 0%, depending on your preference
        success_rates[f"{label} Success Rate"] = success_rate

    backtest_results.append({
        "Stock ID": stock_id,
        "Good Entry": good_entry,
        "Total Purchases": total_trades,
        **success_rates
    })

# Save results
df_backtest = pd.DataFrame(backtest_results)
print("Backtest Summary:")
print(df_backtest)

df_backtest.to_excel(output_file, index=False)
print(f"Backtest summary saved to {output_file}")
