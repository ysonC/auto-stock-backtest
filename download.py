from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from tqdm import tqdm  # Progress bar
import time


def download_stock_data(stock_numbers, start_date):
    # Full path to ChromeDriver
    chromedriver_path = "/Users/w.cheng/Code/auto-stock-backtest/chromedriver"

    # Configure Chrome options for headless mode and downloading
    download_dir = "download"
    Path(download_dir).mkdir(exist_ok=True)  # Ensure download directory exists
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

    # Create a Service object
    service = Service(chromedriver_path)

    # Record start time
    start_time = time.time()

    # Initialize WebDriver with Chrome options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    error_stocks = []  # List to store stocks causing errors

    try:
        total_stocks = len(stock_numbers)

        # Initialize the progress bar
        with tqdm(total=total_stocks, desc="Downloading Stocks", unit="stock") as pbar:
            for index, stock_number in enumerate(stock_numbers, start=1):
                try:
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

                    # print(f"[{index}/{total_stocks}] Downloaded: {stock_number}")

                except Exception as e:
                    print(f"Error while processing stock {stock_number}: {e}")
                    error_stocks.append(stock_number)  # Add stock number to error list

                # Update progress bar
                pbar.update(1)

    finally:
        # Write errors to the log file
        if error_stocks:
            print(f"Error stock number: {error_stocks}")

        # Close the browser
        driver.quit()

        # Record end time
        end_time = time.time()

        # Calculate total time taken
        total_time = end_time - start_time
        print(f"Total time taken for downloading: {total_time:.2f} seconds")
