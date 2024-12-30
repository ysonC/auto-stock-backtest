import subprocess
import sys
import os
import shutil
from pathlib import Path
from halo import Halo
from app import download_chromedriver, download_stock_data, read_stock_numbers_from_file, process_downloaded_stocks, process_stocks


def check_chromedriver():
    """Check if ChromeDriver is installed and accessible."""
    chromedriver_path = Path("setup/chromedriver")
    if not chromedriver_path.exists():
        print("ChromeDriver not found in 'setup/' directory.")
        print("Installing ChromeDriver. . .")
        download_chromedriver()


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
    print("3. Exit")
    choice = input("Enter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        print("Loading stock IDs from input files...")
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
    elif choice == "3":
        print("Program exiting. . .")
        sys.exit(0)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print("----------------------------------------------------")
    print(f"Total stock IDs loaded: {len(stock_numbers)}")
    print(stock_numbers)
    print("----------------------------------------------------")
    return stock_numbers


def main():
    print("Starting the main workflow...")
    check_chromedriver()

    # Input for stock numbers and start date
    print("Getting stock numbers and start date...")
    stock_numbers = get_stock_and_date()

    print("")
    # Step 1: Run the download script with a spinner
    download_stock_data(stock_numbers)

    print("")
    # Step 2: Run the clean stocks script with a spinner
    spinner = Halo(text='Cleaning and processing data...',
                   spinner='line', color='cyan')
    spinner.start()
    try:
        process_downloaded_stocks()
        spinner.succeed("Data cleaned and processed successfully.")
    except Exception as e:
        spinner.fail(f"Failed to clean and process data: {e}")
        print(f"Exception during data cleaning and processing: {e}")

    print("")
    # Step 3: Run the MR backtest script with a spinner
    spinner = Halo(text='Step 3: Performing MR backtesting...',
                   spinner='line', color='cyan')
    spinner.start()
    try:
        # print("Calling process_stocks...")
        process_stocks()
        spinner.succeed("MR backtesting completed successfully.")
    except Exception as e:
        spinner.fail(f"Failed to perform MR backtesting: {e}")
        print(f"Exception during MR backtesting: {e}")


if __name__ == "__main__":
    print("Executing main function...")
    main()
