import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from pathlib import Path
from halo import Halo
import os
from datetime import datetime
from .helpers import *

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input_stock"
DOWNLOAD_DIR = BASE_DIR / "download"
DATA_DIR = BASE_DIR / "data"
STOCK_DATA_DIR = DATA_DIR / "stock_data"

def read_stock_numbers_from_file(file_path):
    """Reads stock numbers from a text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def download_stock_data(stock_numbers):
    start_date = "2001-03-28"
    # Get today's date dynamically
    end_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD

    # Configuration
    chromedriver_path = os.path.join(os.getcwd(), "setup/chromedriver")
    download_dir = DOWNLOAD_DIR
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
        total_stocks = len(stock_numbers)
        for index, stock_number in enumerate(stock_numbers, start=1):
            spinner = Halo(text=f"Processing stock: {stock_number} ({index}/{total_stocks})", spinner='line', color='cyan')
            spinner.start()
            try:
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

                # Save data to a CSV file using pandas
                output_file_path = Path(download_dir) / f"{stock_number}.csv"
                df = pd.DataFrame(data, columns=header)
                save_to_csv(df, output_file_path, False)
                spinner.succeed(f"Stock {stock_number} downloaded successfully.")

            except WebDriverException as e:
                spinner.fail(f"Error while processing stock {stock_number}: {e.msg}")
                error_stocks.append(stock_number)  # Add stock number to error list

    finally:
        # Print any errors
        if error_stocks:
            print(f"Error stock numbers: {error_stocks}")
        # Close the browser
        driver.quit()
    spinner = Halo(text=f"Processing stock: {stock_number} ({index}/{total_stocks})", spinner='line', color='cyan')
    spinner.start()
    spinner.succeed(f"Downloaded ({total_stocks - len(error_stocks)}/{total_stocks}) stocks successfully.")

# Example usage
if __name__ == "__main__":
    stock_file = "input_stock/stock_numbers.txt"  # Input file containing stock numbers
    stock_numbers = read_stock_numbers_from_file(stock_file)
    download_stock_data(stock_numbers)
