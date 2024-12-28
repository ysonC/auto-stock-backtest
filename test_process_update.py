import pandas as pd
from pathlib import Path
import os

# Input and output directories
input_dir = "download"
data_dir = "data"  # Directory to save processed data
# Subdirectory for Date and Price data
date_price_dir = Path(data_dir) / "stock_price"
date_price_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

# Initialize an empty list to collect all summaries
all_summaries = []

# Loop through all CSV files in the `download` directory
for filename in os.listdir(input_dir):
    if filename.endswith(".csv"):  # Process only CSV files
        file_path = os.path.join(input_dir, filename)
        stock_id = filename.split("_")[0]  # Extract stock ID from filename

        # Load CSV file into a DataFrame
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            continue  # Skip this file and move to the next

        # Ensure column names match expectations
        expected_columns = ['Date', 'Price', 'Change', '% Change',
                            'EPS', 'PER', '8X', '9.8X', '11.6X', '13.4X', '15.2X', '17X']
        if not all(col in df.columns for col in expected_columns):
            print(
                f"File {filename} is missing some expected columns: {expected_columns}")
            continue  # Skip this file

        # Extract Date and Price columns and save to a separate file for each stock
        if 'Date' in df.columns and 'Price' in df.columns:
            date_price_df = df[['Date', 'Price']].dropna(
                subset=['Date', 'Price'])
            output_file = date_price_dir / f"{stock_id}"
            date_price_df.to_csv(output_file, index=False)
            print(f"Date and Price data for {stock_id} saved to {output_file}")

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

        median_price = (median_per/latest_per) * \
            latest_closing_price if median_per and latest_per and latest_closing_price else None
        mp_up_down = (median_price - latest_closing_price)/latest_closing_price if median_price and latest_closing_price else None
            
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
            "Min Delta": round(min_delta, 2),
            "####": "####",
            "C$": round(latest_closing_price, 2),
            "M$": round(median_price, 2),
            "T$": "####",
            "MP UpDown": mp_up_down *100
        }

        # Append the summary to the list
        all_summaries.append(summary)

# Convert all summaries to a DataFrame
summary_df = pd.DataFrame(all_summaries)
print("################################################################################################################################################")
print(summary_df)
print("################################################################################################################################################")
# Save the combined summary to an Excel file
output_file = Path(data_dir) / "process_data.xlsx"
summary_df.to_excel(output_file, index=False)

print(f"Processed data has been saved to {output_file}")
