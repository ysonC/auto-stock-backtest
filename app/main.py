import subprocess
import sys
import os
import shutil
from pathlib import Path
from download_stocks import *
from clean_data import *
from backtest_MR import *

def run_script(script_name, args=None):
    """Run a Python script with optional arguments."""
    command = [sys.executable, script_name]
    if args:
        command.extend(args)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script_name}: {result.stderr}")
    else:
        print(result.stdout)

def get_stock_and_date():
    """Get stock numbers either manually or by reading all files in the 'input_stock' directory."""
    # Ensure the input_stock directory exists
    input_dir = Path("input_stock")
    input_dir.mkdir(parents=True, exist_ok=True)

    print("Choose input method for stock numbers:")
    print("1. Load all stock IDs and date from files in 'input_stock' directory")
    print("2. Generate a template file in 'input_stock' directory")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        # Collect stock IDs from all files in the input_stock directory
        stock_numbers = []
        for file in input_dir.iterdir():
            if file.is_file():
                try:
                    with open(file, "r") as f:
                        stock_numbers = read_stock_numbers_from_file(file)     
                except Exception as e:
                    print(f"Error reading file {file.name}: {e}")
        if not stock_numbers:
            print(f"No valid stock IDs found in 'input_stock' directory.")
            sys.exit(1)
    elif choice == "2":
        template_file = input_dir / "stock_numbers.txt"
        with open(template_file, "w") as file:
            file.write("2303\n")
            file.write("2330\n")
        print(f"Template file created: {template_file}")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print("----------------------------------------------------")
    print(f"Total stock IDs loaded: {len(stock_numbers)}")
    print(stock_numbers)
    print("----------------------------------------------------")
    return stock_numbers

def replace_directory(path):
    """"Check and remove old diectory for fresh start"""
    if os.path.exists(path):
        shutil.rmtree(path)
    Path(path).mkdir(parents=True, exist_ok=True)        
        

def main():
    # Ensure the required directories exist
    download_dir = Path("download")
    data_dir = Path("data/stock")
    replace_directory(download_dir)
    replace_directory(data_dir)
    
    # Input for stock numbers and start date
    stock_numbers= get_stock_and_date()
    
    # Step 1: Run the download script
    print("Step 1: Downloads stock data.")
    print("Running download.py...")
    download_stock_data(stock_numbers)
    print("----------------------------------------------------")

    # Step 2: Run the clean stocks script
    print("Step 2: Processes and clean data.")
    print("Running clean_data.py...")
    process_downloaded_stocks()
    print("----------------------------------------------------")

    # Step 3: Run the MR backtest script
    print("Step 3: Performs MR backtesting on the processed data.")
    print("Running backtest_MR.py...")
    process_stocks()
    print("----------------------------------------------------")

if __name__ == "__main__":
    main()
