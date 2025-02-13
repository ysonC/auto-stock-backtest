import pandas as pd
import logging
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from pathlib import Path
from halo import Halo
from app.helpers import *
from app.config import DOWNLOAD_DIR, WEB_CHROMEDRIVER_PATH

MAX_PER = 1000000
MAX_EPS = 1000000

def get_service():
    try:
        if WEB_CHROMEDRIVER_PATH.exists():
            logging.info("Using Heroku's ChromeDriver.")
            return ChromeService(executable_path=str(WEB_CHROMEDRIVER_PATH))
        else:
            logging.warning("Heroku ChromeDriver not found. Falling back to WebDriverManager.")
            return ChromeService(ChromeDriverManager().install())
    except Exception as e:
        logging.error(f"Failed to initialize ChromeDriver service: {e}")
        raise

def read_stock_numbers_from_file(file_path):
    logging.info(f"Reading stock numbers from file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            stock_numbers = [line.strip() for line in f if line.strip()]
            logging.info(f"Loaded {len(stock_numbers)} stock numbers.")
            return stock_numbers
    except Exception as e:
        logging.error(f"Error reading stock numbers from file {file_path}: {e}")
        raise

def is_stock_data_up_to_date(stock_number):
    stock_file = Path(DOWNLOAD_DIR) / f"{stock_number}.csv"
    if not stock_file.exists():
        return False
    try:
        df = pd.read_csv(stock_file)
        if df.empty:
            return False
        df["ParsedDate"] = df["Date"].apply(parse_custom_date)
        if df["ParsedDate"].isnull().all():
            return False
        return df["ParsedDate"].max() >= get_most_recent_friday()
    except Exception as e:
        logging.error(f"Error reading stock file {stock_file}: {e}")
        return False

def download_data(stock_numbers, data_type):
    logging.info(f"Starting {data_type} stock data download.")
    start_date = "2001-03-28"
    end_date = datetime.now().strftime("%Y-%m-%d")
    create_folder(DOWNLOAD_DIR)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    prefs = {"download.default_directory": str(Path(DOWNLOAD_DIR).resolve())}
    chrome_options.add_experimental_option("prefs", prefs)

    service = get_service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    error_stocks = []
    url_template = {
        "shareholder": "https://goodinfo.tw/tw/EquityDistributionClassHis.asp?STEP=DATA&STOCK_ID={}&CHT_CAT=WEEK&PRICE_ADJ=F&START_DT={}&END_DT={}",
        "stocks": "https://goodinfo.tw/tw/ShowK_ChartFlow.asp?RPT_CAT=PER&STEP=DATA&STOCK_ID={}&CHT_CAT=WEEK&PRICE_ADJ=F&START_DT={}&END_DT={}"
    }
    headers = {
        "shareholder": ["Date", "End Date", "Price", "Change", "% Change", "Inventory", "<=10", ">10<=50", ">50<=100", ">100<=200", ">200<=400", ">400<=800", ">800<=1000", ">1000"],
        "stocks": ["Date", "Price", "Change", "% Change", "EPS", "PER", "8X", "9.8X", "11.6X", "13.4X", "15.2X", "17X"]
    }
    
    try:
        for stock_number in stock_numbers:
            spinner = Halo(text=f"Processing {data_type} stock: {stock_number}", spinner="line", color="cyan")
            spinner.start()
            try:
                driver.delete_all_cookies()
                driver.get(url_template[data_type].format(stock_number, start_date, end_date))
                
                WebDriverWait(driver, 5).until(lambda d: d.find_element(By.ID, "tblDetail"))
                table_html = driver.execute_script("return document.getElementById('tblDetail').innerHTML")
                
                soup = BeautifulSoup(table_html, "html.parser")
                rows = soup.find_all("tr")
                data = [[cell.get_text(strip=True) for cell in row.find_all("td")] for row in rows[1:] if row]
                df = pd.DataFrame(data, columns=headers[data_type])
                df = df.dropna(how="all")
                df = df[~df["Date"].str.endswith("W53")]
                
                if data_type == "stocks":
                    df["EPS"] = pd.to_numeric(df["EPS"], errors="coerce")
                    df["PER"] = pd.to_numeric(df["PER"], errors="coerce")
                    df.loc[df["EPS"] > MAX_EPS, "EPS"] = None
                    df.loc[df["PER"] > MAX_PER, "PER"] = None
                
                save_to_csv(df, Path(DOWNLOAD_DIR) / f"{data_type}_{stock_number}.csv", False)
                spinner.succeed(f"{data_type.capitalize()} stock {stock_number} downloaded successfully.")
            except Exception as e:
                spinner.fail(f"Error processing {data_type} stock {stock_number}")
                logging.error(f"Error downloading {data_type} data for {stock_number}: {e}")
                error_stocks.append(stock_number)
    finally:
        driver.quit()
        logging.info(f"{data_type.capitalize()} download process completed.")
    return error_stocks

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    stock_numbers = read_stock_numbers_from_file("input_stock/stock_numbers.txt")
    download_data(stock_numbers, "shareholder")
    download_data(stock_numbers, "stocks")

