import os
import pandas as pd
import numpy as np

# Folder containing stock CSV files
FOLDER_PATH = "app/data/raw"
OUTPUT_FILE = "analysis_results.csv"

def analyze_all_stocks(folder_path, output_file):
    summary_data = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(folder_path, file_name)
            ticker = file_name.replace(".csv", "")

            try:
                # Load stock data
                stock_data = pd.read_csv(file_path)

                # Extract required columns
                stock_data["PER"] = pd.to_numeric(stock_data.get("PER", np.nan), errors="coerce")
                stock_data["Price"] = pd.to_numeric(stock_data.get("Price", np.nan), errors="coerce")

                # Ensure valid PER data
                stock_data = stock_data.dropna(subset=["PER"])
                if stock_data.empty:
                    raise ValueError(f"No valid PER data for ticker {ticker}")

                # Current PER and Price
                current_per = stock_data["PER"].iloc[-1]
                current_price = stock_data["Price"].iloc[-1]

                # Statistics
                gep25 = np.percentile(stock_data["PER"], 25)
                gep_med = np.median(stock_data["PER"])
                min_per = stock_data["PER"].min()
                max_per = stock_data["PER"].max()
                mean_per = stock_data["PER"].mean()

                # Deltas
                delta25 = (current_per - gep25) / (max_per - min_per) if max_per != min_per else np.nan
                delta_med = (current_per - gep_med) / (max_per - min_per) if max_per != min_per else np.nan
                delta_mean = (current_per - mean_per) / (max_per - min_per) if max_per != min_per else np.nan
                delta_min = (current_per - min_per) / (max_per - min_per) if max_per != min_per else np.nan

                # Mean Reversion Logic
                one_month_mr, one_month_cases = mean_reversion_calculation(stock_data, 4, gep_med, gep25)
                two_month_mr, two_month_cases = mean_reversion_calculation(stock_data, 8, gep_med, gep25)
                three_month_mr, three_month_cases = mean_reversion_calculation(stock_data, 12, gep_med, gep25)
                avg_mr = np.mean([one_month_mr, two_month_mr, three_month_mr])

                # Output Results
                summary_data.append({
                    "Ticker": ticker,
                    "Current PER": current_per,
                    "GEP.25": round(gep25, 2),
                    "GEP.MED": round(gep_med, 2),
                    "Min PER": round(min_per, 2),
                    "Max PER": round(max_per, 2),
                    "5Y Mean": round(mean_per, 2),
                    "25 Delta": round(delta25, 2) if not np.isnan(delta25) else "N/A",
                    "MED Delta": round(delta_med, 2) if not np.isnan(delta_med) else "N/A",
                    "Mean Delta": round(delta_mean, 2) if not np.isnan(delta_mean) else "N/A",
                    "Min Delta": round(delta_min, 2) if not np.isnan(delta_min) else "N/A",
                    "1M MR": round(one_month_mr, 4)*100,
                    "2M MR": round(two_month_mr, 4)*100,
                    "3M MR": round(three_month_mr, 4)*100,
                    "Avg MR": round(avg_mr, 2),
                    "1M Incident": one_month_cases,
                    "2M Incident": two_month_cases,
                    "3M Incident": three_month_cases
                })

            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

    # Save to output CSV
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)
    print(f"Analysis saved to {output_file}")


def mean_reversion_calculation(data, weeks, median_per, quartile_per):
    """
    Calculate mean reversion success rate and total cases.
    """
    total_cases = 0
    successful_cases = 0

    for i in range(len(data) - weeks):
        start_per = data["PER"].iloc[i]
        if start_per > quartile_per:
            continue

        total_cases += 1
        initial_deviation = abs(start_per - median_per)

        for j in range(1, weeks + 1):
            future_per = data["PER"].iloc[i + j]
            if abs(future_per - median_per) < initial_deviation:
                successful_cases += 1
                break

    success_rate = (successful_cases / total_cases) if total_cases > 0 else 0
    return success_rate, total_cases


# Run the analysis
analyze_all_stocks(FOLDER_PATH, OUTPUT_FILE)
