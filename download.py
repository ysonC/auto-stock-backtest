from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import sys

# Retrieve stock numbers and start date from arguments
if len(sys.argv) < 3:
    print("Usage: download.py <stock_numbers> <start_date>")
    sys.exit(1)

stock_numbers = sys.argv[1].split(",")
start_date = sys.argv[2]

# Full path to ChromeDriver
chromedriver_path = "/home/yson/coding/auto-stock-backtest/chromedriver"

# Configure Chrome options for headless mode and downloading
download_dir = "download"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
prefs = {
    "download.default_directory": str(Path(download_dir).resolve()),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Create a Service object
service = Service(chromedriver_path)

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    total_stocks = len(stock_numbers)
    for index, stock_number in enumerate(stock_numbers, start=1):
        print(f"[{index}/{total_stocks}] Processing stock: {stock_number}")

        # Open the webpage with the current stock number
        driver.get(f"https://goodinfo.tw/tw/ShowK_ChartFlow.asp?RPT_CAT=PER&STOCK_ID={stock_number}")

        # Wait for the element `divDetail` to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "divDetail"))
        )

        # Set the value of start time
        driver.execute_script(f"document.getElementById('edtSTART_TIME').value = '{start_date}';")

        # Reload the details
        driver.execute_script("ReloadDetail();")
        
        # Wait for the `divK_ChartFlowDetail` to reload
        time.sleep(2)
        
        # Execute JavaScript to trigger the download button
        driver.execute_script("export2html(divDetail.innerHTML, 'K_ChartFlow.html');")

        # Wait for the file to download by checking if the file exists in the download directory
        downloaded_file = Path(download_dir) / "K_ChartFlow.html"
        WebDriverWait(driver, 20).until(lambda d: downloaded_file.exists())

        # Rename the file to the stock number
        new_file_name = Path(download_dir) / f"{stock_number}.html"
        downloaded_file.rename(new_file_name)
        
        print(f"[{index}/{total_stocks}] Downloaded: {stock_number}")


finally:
    # Close the browser
    driver.quit()
