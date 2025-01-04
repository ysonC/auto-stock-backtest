from pathlib import Path

# Define the base directory dynamically (root of your project)
BASE_DIR = Path(__file__).resolve().parent

# 'app' is the base of this substructure
APP_DIR = BASE_DIR  

# Paths to key directories
DATA_DIR = APP_DIR / "data"
STOCK_DATA_DIR = DATA_DIR / "stock_data"
RESULTS_DIR = DATA_DIR / "results"
DOWNLOAD_DIR = DATA_DIR / "raw"
RESOURCES_DIR = BASE_DIR.parent / "resources"
INPUT_STOCK_DIR = APP_DIR / "input_stock"
LOGS_DIR = BASE_DIR.parent / "logs"

# Paths to specific files
PROCESS_DATA_PATH = RESULTS_DIR / "process_data.csv"
OUTPUT_DATA_PATH = RESULTS_DIR / "backtest_MR_data.csv"
STOCK_NUMBERS_PATH = INPUT_STOCK_DIR / "stock_numbers.txt"

# ChromeDriver path
CHROMEDRIVER_PATH = RESOURCES_DIR / "chromedriver"
WEB_CHROMEDRIVER_PATH = ".chrome-for-testing/chromedriver-linux64/chromedriver"
GOOGLE_CHROME_BIN = APP_DIR / ".chrome-for-testing/chrome-linux/chrome"

# Debug: Print paths to verify correctness during setup
if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"APP_DIR: {APP_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"STOCK_DATA_DIR: {STOCK_DATA_DIR}")
    print(f"RESULTS_DIR: {RESULTS_DIR}")
    print(f"DOWNLOAD_DIR: {DOWNLOAD_DIR}")
    print(f"RESOURCES_DIR: {RESOURCES_DIR}")
    print(f"INPUT_STOCK_DIR: {INPUT_STOCK_DIR}")
    print(f"LOGS_DIR: {LOGS_DIR}")

    print(f"PROCESS_DATA_PATH: {PROCESS_DATA_PATH}")
    print(f"OUTPUT_DATA_PATH: {OUTPUT_DATA_PATH}")
    print(f"STOCK_NUMBERS_PATH: {STOCK_NUMBERS_PATH}")
    print(f"WEB_CHROMEDRIVER_PATH: {WEB_CHROMEDRIVER_PATH}")
    print(f"CHROMEDRIVER_PATH: {CHROMEDRIVER_PATH}")
