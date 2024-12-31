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
from datetime import datetime
from .helpers import *
from .config import DOWNLOAD_DIR, CHROMEDRIVER_PATH, STOCK_DATA_DIR

def read_stock_numbers_from_file(file_path):
    """Reads stock numbers from a text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]
    
def parse_custom_date(custom_date):
    """Converts custom date format (24W52) to a standard YYYY-MM-DD format."""
    try:
        # Extract year and week from the custom date
        year = int("20" + custom_date[:2])  # Assumes year is 20XX
        week = int(custom_date[3:])  # Extract the week number

        # Convert to a standard date (Monday of the given week)
        return datetime.strptime(f"{year}-W{week}-1", "%Y-W%U-%w")
    except Exception as e:
        print(f"Error parsing date '{custom_date}': {e}")
        return None

def is_stock_data_up_to_date(stock_number):
    """Check if the stock data exists, contains valid data, and is up-to-date."""
    stock_file = Path(STOCK_DATA_DIR) / f"{stock_number}.csv"
    if not stock_file.exists():
        return False  # File does not exist, download needed

    try:
        # Load the CSV and check if it contains valid data
        df = pd.read_csv(stock_file)
        if df.empty:
            return False  # File is empty, download needed

        # Parse the custom date column
        df['ParsedDate'] = df['Date'].apply(parse_custom_date)
        if df['ParsedDate'].isnull().all():
            return False  # No valid dates found, download needed

        # Get the latest date in the file
        latest_date_in_file = df['ParsedDate'].max()

        # Get the current date
        current_date = datetime.now()

        # Check if the latest date in the file is earlier than today
        if latest_date_in_file < current_date:
            return False  # Data is outdated, download needed

        return True  # Data is valid and up-to-date
    except Exception as e:
        print(f"Error reading {stock_file}: {e}")
        return False  # Any error means we need to re-download


def download_stock_data(stock_numbers):
    start_date = "2001-03-28"
    # Get today's date dynamically
    end_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD

    # Configuration
    create_folder(DOWNLOAD_DIR)

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    prefs = {
        "download.default_directory": str(Path(DOWNLOAD_DIR).resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize WebDriver
    service = Service(CHROMEDRIVER_PATH)
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
                output_file_path = Path(DOWNLOAD_DIR) / f"{stock_number}.csv"
                df = pd.DataFrame(data, columns=header)
                save_to_csv(df, output_file_path, False)
                spinner.succeed(f"Stock {stock_number} downloaded successfully.")

            except Exception as e:
                spinner.fail(f"Error while processing stock {stock_number}: {e}")
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

def check_and_download_stocks(stock_numbers):
    """Check stocks and download only if needed."""
    stocks_to_download = []

    spinner = Halo(text='Checking to update stock data...', spinner='line', color='cyan')
    spinner.start()
    for stock_number in stock_numbers:
        if not is_stock_data_up_to_date(stock_number):
            stocks_to_download.append(stock_number)
        # else:
        #     print(f"Stock {stock_number} is already up to date.")
    if len(stocks_to_download) == 0:
        spinner.succeed("All stocks are up to date. No download needed.")
    else:
        spinner.warn(f"Found {len(stocks_to_download)} stocks to download.")    

    if stocks_to_download:
        # print(f"Downloading data for {len(stocks_to_download)} stocks: {stocks_to_download}")
        download_stock_data(stocks_to_download)
    # else:
    #     print("All stocks are up to date. No download needed.")

# Example usage
if __name__ == "__main__":
    stock_file = "input_stock/stock_numbers.txt"  # Input file containing stock numbers
    stock_numbers = read_stock_numbers_from_file(stock_file)
    download_stock_data(stock_numbers)
