import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pathlib import Path
from halo import Halo
from datetime import datetime
import logging
from .helpers import *
from .config import DOWNLOAD_DIR, CHROMEDRIVER_PATH


def read_stock_numbers_from_file(file_path):
    """Reads stock numbers from a text file."""
    logging.info(f"Reading stock numbers from file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            stock_numbers = [line.strip() for line in f if line.strip()]
            logging.info(f"Loaded {len(stock_numbers)} stock numbers.")
            return stock_numbers
    except Exception as e:
        logging.error(
            f"Error reading stock numbers from file {file_path}: {e}")
        raise


def parse_custom_date(custom_date):
    """Converts custom date format (24W52) to a standard YYYY-MM-DD format."""
    try:
        year = int("20" + custom_date[:2])  # Assumes year is 20XX
        week = int(custom_date[3:])  # Extract the week number
        return datetime.strptime(f"{year}-W{week}-1", "%Y-W%U-%w")
    except Exception as e:
        logging.warning(f"Error parsing date '{custom_date}': {e}")
        return None


def is_stock_data_up_to_date(stock_number):
    """Check if the stock data exists, contains valid data, and is up-to-date."""
    stock_file = Path(DOWNLOAD_DIR) / f"{stock_number}.csv"
    logging.info(
        f"Checking if stock data is up-to-date for stock: {stock_number}")
    if not stock_file.exists():
        logging.info(
            f"Stock file {stock_file} does not exist. Download needed.")
        return False

    try:
        df = pd.read_csv(stock_file)
        if df.empty:
            logging.info(f"Stock file {stock_file} is empty. Download needed.")
            return False

        df['ParsedDate'] = df['Date'].apply(parse_custom_date)
        if df['ParsedDate'].isnull().all():
            logging.info(
                f"No valid dates found in stock file {stock_file}. Download needed.")
            return False

        latest_date_in_file = df['ParsedDate'].max()
        current_date = datetime.now()

        if latest_date_in_file < current_date:
            logging.info(
                f"Data in {stock_file} is outdated. Latest date: {latest_date_in_file}")
            return False

        logging.info(f"Stock data for {stock_number} is up-to-date.")
        return True
    except Exception as e:
        logging.error(f"Error reading stock file {stock_file}: {e}")
        return False


def download_stock_data(stock_numbers):
    logging.info("Starting stock data download.")
    start_date = "2001-03-28"
    end_date = datetime.now().strftime("%Y-%m-%d")

    create_folder(DOWNLOAD_DIR)

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

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    header = ['Date', 'Price', 'Change', '% Change', 'EPS',
              'PER', '8X', '9.8X', '11.6X', '13.4X', '15.2X', '17X']
    error_stocks = []

    try:
        total_stocks = len(stock_numbers)
        for index, stock_number in enumerate(stock_numbers, start=1):
            spinner = Halo(
                text=f"Processing stock: {stock_number} ({index}/{total_stocks})", spinner='line', color='cyan')
            spinner.start()
            try:
                driver.delete_all_cookies()
                url = f"https://goodinfo.tw/tw/ShowK_ChartFlow.asp?RPT_CAT=PER&STEP=DATA&STOCK_ID={stock_number}&CHT_CAT=WEEK&PRICE_ADJ=F&START_DT={start_date}&END_DT={end_date}"
                driver.get(url)

                WebDriverWait(driver, 2).until(
                    lambda d: d.find_element(By.ID, "tblDetail"))
                table_html = driver.execute_script(
                    "return document.getElementById('tblDetail').innerHTML")

                soup = BeautifulSoup(table_html, "html.parser")
                rows = soup.find_all("tr")
                data = [[cell.get_text(strip=True) for cell in row.find_all(
                    "td")] for row in rows[1:] if row]

                output_file_path = Path(DOWNLOAD_DIR) / f"{stock_number}.csv"
                df = pd.DataFrame(data, columns=header)
                df = df.dropna(how='all')
                save_to_csv(df, output_file_path, False)
                logging.info(
                    f"Downloaded and saved data for stock {stock_number} to {output_file_path}.")
                spinner.succeed(
                    f"Stock {stock_number} downloaded successfully.")
            except Exception as e:
                spinner.fail(f"Error processing stock {stock_number}")
                logging.error(
                    f"Error downloading data for stock {stock_number}: {e}")
                error_stocks.append(stock_number)
    finally:
        if error_stocks:
            logging.warning(f"Stocks with errors: {error_stocks}")
        driver.quit()
        logging.info("Download process completed.")


def check_and_download_stocks(stock_numbers):
    logging.info("Checking and downloading stocks as needed.")
    spinner = Halo(text="Checking stock data...", spinner='line', color='cyan')
    spinner.start()
    stocks_to_download = [
        s for s in stock_numbers if not is_stock_data_up_to_date(s)]

    if stocks_to_download:
        if len(stocks_to_download) > 10:
            spinner.info(f"{len(stocks_to_download)} Stocks to download")
        else:
            spinner.info(
                f"{len(stocks_to_download)} Stocks to download: {stocks_to_download}")
        logging.info(f"Stocks to download: {stocks_to_download}")
        download_stock_data(stocks_to_download)
    else:
        spinner.succeed("All stocks checked, no download required.")
        logging.info("All stocks are up-to-date.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logging.info("Script execution started.")
    try:
        stock_file = "input_stock/stock_numbers.txt"
        stock_numbers = read_stock_numbers_from_file(stock_file)
        check_and_download_stocks(stock_numbers)
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True)
    logging.info("Script execution finished.")
