import pandas as pd
from pathlib import Path
import os

# Input and output directories
input_dir = "download"
data_dir = "data"  # Directory to save processed data
Path(data_dir).mkdir(parents=True, exist_ok=True)  # Ensure directory exists

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
        expected_columns = ['Date', 'Price', 'Change', '% Change', 'EPS', 'PER', '8X', '9.8X', '11.6X', '13.4X', '15.2X', '17X']
        if not all(col in df.columns for col in expected_columns):
            print(f"File {filename} is missing some expected columns: {expected_columns}")
            continue  # Skip this file

        # Calculate required values
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['PER'] = pd.to_numeric(df['PER'], errors='coerce')

        latest_row = df.iloc[0]  # Assuming the first row contains the latest data
        latest_per = latest_row['PER']
        latest_closing_price = latest_row['Price']

        # Drop rows with NaN in 'PER' for further calculations
        df_clean = df.dropna(subset=['PER'])

        average_per = df_clean['PER'].mean() if not df_clean.empty else None
        minimum_per = df_clean['PER'].min() if not df_clean.empty else None
        top_price = df_clean['Price'].max() if not df_clean.empty else None
        quartile_per = df_clean['PER'].quantile(0.25) if not df_clean.empty else None

        gep_delta = latest_per - quartile_per if latest_per and quartile_per else None
        min_delta = latest_per - minimum_per if latest_per and minimum_per else None
        avg_delta = latest_per - average_per if latest_per and average_per else None

        # Create a summary for this stock
        summary = {
            "Stock ID": stock_id,
            "Current PER": latest_per,
            "Good Entry": quartile_per,
            "Minimum PER": minimum_per,
            "Average PER": average_per,
            "Latest Closing Price": latest_closing_price,
            "Top Price": top_price,
            "GEP Delta": gep_delta,
            "Minimum Delta": min_delta,
            "Average Delta": avg_delta,
        }

        # Append the summary to the list
        all_summaries.append(summary)

# Convert all summaries to a DataFrame
summary_df = pd.DataFrame(all_summaries)

# Save the combined summary to an Excel file
output_file = Path(data_dir) / "process_data.xlsx"
summary_df.to_excel(output_file, index=False)

print(f"Processed data has been saved to {output_file}")
