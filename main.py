import subprocess
import sys
import os
import shutil
from pathlib import Path

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

def get_stock_numbers():
    """Get stock numbers either manually or by reading all files in the 'input_stock' directory."""
    # Ensure the input_stock directory exists
    input_dir = Path("input_stock")
    input_dir.mkdir(parents=True, exist_ok=True)

    print("Choose input method for stock numbers:")
    print("1. Enter manually")
    print("2. Load all stock IDs from files in 'input_stock' directory")
    print("3. Generate a template file in 'input_stock' directory")
    choice = input("Enter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        stock_numbers = input("Enter a comma-separated list of stock IDs: ").split(",")
    elif choice == "2":
        # Collect stock IDs from all files in the input_stock directory
        stock_numbers = []
        for file in input_dir.iterdir():
            if file.is_file():
                try:
                    with open(file, "r") as f:
                        file_stock_numbers = [line.strip() for line in f if line.strip()]
                        stock_numbers.extend(file_stock_numbers)
                        # print(f"Loaded {len(file_stock_numbers)} stock IDs from {file.name}")
                except Exception as e:
                    print(f"Error reading file {file.name}: {e}")
        if not stock_numbers:
            print(f"No valid stock IDs found in 'input_stock' directory.")
            sys.exit(1)
    elif choice == "3":
        template_file = input_dir / "template_stock_ids.txt"
        with open(template_file, "w") as file:
            file.write("2303\n")
            file.write("2330\n")
        print(f"Template file created: {template_file}")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print(f"Total stock IDs loaded: {len(stock_numbers)}")
    print(stock_numbers)
    return stock_numbers

def replace_directory(path):
    """"Check and remove old diectory for fresh start"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
        
        

def main():
    # Input for stock numbers and start date
    stock_numbers = get_stock_numbers()
    start_date = input("Enter the start date (YYYY-MM-DD): ")

    # Ensure the required directories exist
    download_dir = Path("download")
    data_dir = Path("data/stock")
    replace_directory(download_dir)
    replace_directory(data_dir)
    
    # Step 1: Run the download script
    print("Running download.py...")
    run_script("download.py", args=[",".join(stock_numbers), start_date])

    # Step 2: Run the extract_data script
    print("Running extract_data.py...")
    run_script("extract_data.py")

    # Step 3: Run the process script
    print("Running process.py...")
    run_script("process.py")

    # Step 4: Run the backtest script
    print("Running backtest.py...")
    run_script("backtest.py")

if __name__ == "__main__":
    main()
