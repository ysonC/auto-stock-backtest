import subprocess
import sys
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

def main():
    # Input for stock list and start date
    stock_numbers = input("Enter a comma-separated list of stock IDs: ").split(",")
    start_date = input("Enter the start date (YYYY-MM-DD): ")

    # Ensure the required directories exist
    download_dir = Path("download")
    data_dir = Path("data/stock")
    download_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

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
