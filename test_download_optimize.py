from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup  # For parsing HTML efficiently
from pathlib import Path
import csv

# Configuration
chromedriver_path = "/home/yson/coding/auto-stock-backtest/chromedriver"
download_dir = "download"
stock_number = "2303"
start_date = "2021-02-02"
end_date = "2024-12-01"
url = f"https://goodinfo.tw/tw/ShowK_ChartFlow.asp?RPT_CAT=PER&STEP=DATA&STOCK_ID={stock_number}&CHT_CAT=WEEK&PRICE_ADJ=F&START_DT={start_date}&END_DT={end_date}"

# Hardcoded header
header = ['Date', 'Price', 'Change', '% Change', 'EPS', 'PER', '8X', '9.8X', '11.6X', '13.4X', '15.2X', '17X']

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

try:
    # Open the webpage
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

    # Print extracted data for debugging
    print("Hardcoded Header:")
    print(header)
    print("\nData:")
    for row in data:
        print(row)

    # Save data to a CSV file with hardcoded header
    output_file = Path(download_dir) / f"{stock_number}_stock_data.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write hardcoded header
        writer.writerows(data)  # Write data rows

    print(f"Stock data saved to {output_file}")

finally:
    driver.quit()
