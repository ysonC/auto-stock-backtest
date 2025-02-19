import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # For parsing HTML efficiently
from pathlib import Path
from tqdm import tqdm
import csv
import os
from datetime import datetime  # For dynamic date

def download_stock_data(stock_numbers, start_date):
    # Get today's date dynamically
    end_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD

    # Configuration
    chromedriver_path = os.path.join(os.getcwd(), "setup/chromedriver")
    download_dir = "download"
    Path(download_dir).mkdir(exist_ok=True)  # Ensure download directory exists

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    prefs = {
        "download.default_directory": str(Path(download_dir).resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize WebDriver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Hardcoded header
    header = ['Date', 'Price', 'Change', '% Change', 'EPS', 'PER', '8X', '9.8X', '11.6X', '13.4X', '15.2X', '17X']

    error_stocks = []  # List to store stocks causing errors

    try:
        # Progress bar for downloading multiple stocks
        total_stocks = len(stock_numbers)
        with tqdm(total=total_stocks, desc="Downloading Stocks", unit="stock") as pbar:
            for index, stock_number in enumerate(stock_numbers, start=1):
                try:
                    print(f"[{index}/{total_stocks}] Processing stock: {stock_number}")

                    # Reset cookies
                    driver.delete_all_cookies()
                    
                    # Open the webpage
                    url = f"https://goodinfo.tw/tw/ShowK_ChartFlow.asp?RPT_CAT=PER&STEP=DATA&STOCK_ID={stock_number}&CHT_CAT=WEEK&PRICE_ADJ=F&START_DT={start_date}&END_DT={end_date}"
                    driver.get(url)
                    
                    # Wait for the table to load
                    WebDriverWait(driver, 10).until(
                        lambda d: d.find_element(By.ID, "tblDetail")
                    )

                    # Use JavaScript to fetch the table's innerHTML
                    table_html = driver.execute_script(
                        "return document.getElementById('tblDetail').innerHTML"
                    )

                    # Parse the table with BeautifulSoup
                    soup = BeautifulSoup(table_html, "html.parser")
                    rows = soup.find_all("tr")

                    # Extract data rows, skipping header
                    data = []
                    for row in rows[1:]:  # Skip header row
                        cells = [cell.get_text(strip=True) for cell in row.find_all("td") if cell.get_text(strip=True)]
                        if cells:
                            data.append(cells)

                    # Save data to a CSV file
                    output_file = Path(download_dir) / f"{stock_number}.csv"
                    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(header)  # Write hardcoded header
                        writer.writerows(data)  # Write data rows

                except Exception as e:
                    print(f"Error while processing stock {stock_number}: {e}")
                    error_stocks.append(stock_number)  # Add stock number to error list

                # Update progress bar
                pbar.update(1)

    finally:
        # Print any errors
        if error_stocks:
            print(f"Error stock numbers: {error_stocks}")

        # Close the browser
        driver.quit()

    print("All stock data downloaded!")
    
    
# Path to the Excel file
excel_file_path = "Wyson.xlsx"

# Load the Excel file and specify the relevant sheet
data_df = pd.read_excel(excel_file_path)

# Extract stock tickers from the "Ticker" column
stock_tickers = data_df["Ticker"].dropna().tolist()

# Print or use the list of stock tickers
print(stock_tickers)