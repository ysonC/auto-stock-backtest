from pathlib import Path

# Define the base directory dynamically (root of your project)
BASE_DIR = Path(__file__).resolve().parent

# Paths to key directories
APP_DIR = BASE_DIR  # 'app' is the base of this substructure
DATA_DIR = APP_DIR / "data"
DOWNLOAD_DIR = APP_DIR / "download"
RESOURCES_DIR = BASE_DIR.parent / "resources"  # Ensure it's pointing to the correct location
INPUT_STOCK_DIR = BASE_DIR.parent / "input_stock"

# Specific directories
STOCK_DATA_DIR = DATA_DIR / "stock_data"

# Paths to specific files
PROCESS_DATA_PATH = DATA_DIR / "process_data.csv"
OUTPUT_DATA_PATH = DATA_DIR / "backtest_MR_data.csv"
STOCK_NUMBERS_PATH = INPUT_STOCK_DIR / "stock_numbers.txt"

# ChromeDriver path
CHROMEDRIVER_PATH = RESOURCES_DIR / "chromedriver"

# Debug: Print paths to verify correctness during setup
if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"STOCK_DATA_DIR: {STOCK_DATA_DIR}")
    print(f"PROCESS_DATA_PATH: {PROCESS_DATA_PATH}")
    print(f"OUTPUT_DATA_PATH: {OUTPUT_DATA_PATH}")
    print(f"CHROMEDRIVER_PATH: {CHROMEDRIVER_PATH}")
    print(f"INPUT_STOCK_DIR: {INPUT_STOCK_DIR}")
