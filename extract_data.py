import os
import pandas as pd
from bs4 import BeautifulSoup

# Directories
download_dir = "download"
output_dir = "data/stock"
os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

# Parse each HTML file in the download directory
for filename in os.listdir(download_dir):
    if filename.endswith(".html"):
        stock_id = filename.split(".")[0]  # Extract stock ID from filename
        file_path = os.path.join(download_dir, filename)

        # Initialize a list to store the extracted data for this stock
        extracted_data = []

        # Parse the HTML file
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        
        # Find the data table
        table = soup.find("table", {"id": "tblDetail"})
        if not table:
            print(f"No table found in file {filename}, skipping.")
            continue
        
        # Extract rows of the table
        rows = table.find_all("tr")[2:]  # Skip header rows
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                try:
                    # Check if any required field is empty
                    date = cols[0].text.strip()
                    closing_price_text = cols[1].text.strip()
                    eps_text = cols[4].text.strip()
                    per_text = cols[5].text.strip()
                    
                    if not closing_price_text or not per_text:
                        continue  # Skip rows with empty values
                    
                    # Convert to float
                    closing_price = float(closing_price_text)
                    eps = float(eps_text)
                    per = float(per_text)
                    
                    # Append the extracted data
                    extracted_data.append({
                        "Date": date,
                        "Closing Price": closing_price,
                        "PER": per
                    })
                except ValueError as e:
                    print(f"Error parsing row in file {filename}: {e}")
                    continue
        
        # Save the extracted data to an Excel file for this stock
        if extracted_data:
            output_file = os.path.join(output_dir, f"{stock_id}_price.xlsx")
            df = pd.DataFrame(extracted_data)
            df.to_excel(output_file, index=False)
            print(f"Extracted data for Stock ID {stock_id} saved to {output_file}")
