from bs4 import BeautifulSoup
import os
import pandas as pd

# Directory containing the HTML files
download_dir = "download"

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

# Initialize a list to store data
data = []

# Parse all HTML files in the directory
for filename in os.listdir(download_dir):
    if filename.endswith(".html"):
        stock_id = filename.split(".")[0]  # Extract stock number from the filename
        file_path = os.path.join(download_dir, filename)
        
        # Read and parse the HTML file
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            
            # Find the table containing EPS, PER, and closing price data
            table = soup.find("table", {"id": "tblDetail"})
            if table:
                rows = table.find_all("tr")[2:]  # Skip header rows
                
                eps_values = []
                per_values = []
                price_values = []
                latest_closing_price = None  # Initialize latest closing price
                latest_per = None  # Initialize the latest PER
                
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 6:
                        try:
                            # Extract EPS, PER, and prices
                            eps = float(cols[4].text.strip())
                            per = float(cols[5].text.strip())
                            price = float(cols[1].text.strip())  # Assuming price is in the second column
                            eps_values.append(eps)
                            per_values.append(per)
                            price_values.append(price)
                            
                            # Extract the latest closing price and PER (first row is the latest)
                            if latest_closing_price is None:
                                latest_closing_price = price
                                latest_per = per
                        except ValueError:
                            continue
                
                # Calculate averages, minimum PER, top price, and 25th percentile if data is available
                avg_per = sum(per_values) / len(per_values) if per_values else None
                min_per = min(per_values) if per_values else None
                top_price = max(price_values) if price_values else None
                quartile_per = pd.Series(per_values).quantile(0.25) if per_values else None
                gep_delta = latest_per - quartile_per
                # Calculate Delta values
                min_delta = latest_per - min_per if latest_per and min_per else None
                avg_delta = latest_per - avg_per if latest_per and avg_per else None
                
                # Append to data
                data.append({
                    "Stock ID": stock_id,
                    "Current PER": latest_per,
                    "Good Entry": quartile_per,
                    "Minimum PER": min_per,
                    "Average PER": avg_per,
                    "Latest Closing Price": latest_closing_price,
                    "Top Price": top_price,
                    "GEP Delta": gep_delta,
                    "Minimum Delta": min_delta,
                    "Average Delta": avg_delta
                })

# Create a DataFrame and display the results
df = pd.DataFrame(data)
print(df)

# Save the DataFrame to an Excel file
output_file = os.path.join(data_dir, "process_data.xlsx")
df.to_excel(output_file, index=False)

print(f"Data has been saved to {output_file}")