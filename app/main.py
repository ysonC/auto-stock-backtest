import sys
from pathlib import Path
from halo import Halo
from app import (
    download_chromedriver, 
    read_stock_numbers_from_file, 
    check_and_download_stocks,
    process_downloaded_stocks, 
    process_stocks,
    create_folder,
    CHROMEDRIVER_PATH,
    DATA_DIR,
    INPUT_STOCK_DIR,
    RESULTS_DIR,
    STOCK_DATA_DIR,
    DOWNLOAD_DIR,
    RESOURCES_DIR
    )

def check_all_folders():
    """Check if all necessary folders exist."""
    folders = [DATA_DIR, INPUT_STOCK_DIR, RESULTS_DIR, STOCK_DATA_DIR, DOWNLOAD_DIR, RESOURCES_DIR]
    for folder in folders:
        create_folder(folder)

def check_chromedriver():
    """Check if ChromeDriver is installed and accessible."""
    if not CHROMEDRIVER_PATH.exists():
        print("ChromeDriver not found in 'setup/' directory.")
        print("Installing ChromeDriver. . .")
        download_chromedriver()

def get_stock_numbers():
    """Get stock numbers either manually or by reading all files in the 'input_stock' directory."""
    # Ensure the input_stock directory exists
    input_dir = Path("input_stock")
    input_dir.mkdir(parents=True, exist_ok=True)

    print("Choose input method for stock numbers:")
    print("1. Load all stock IDs and date from files in 'input_stock' directory")
    print("2. Generate a template file in 'input_stock' directory")
    print("3. Exit")
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    print("")
    
    spinner = Halo(text='Loading stock IDs from input files...', spinner='line', color='cyan')
    spinner.start()
    
    if choice == "1":
        # print("Loading stock IDs from input files...")
        stock_numbers = []
        for file in input_dir.iterdir():
            if file.is_file():
                try:
                    with open(file, "r") as f:
                        stock_numbers = read_stock_numbers_from_file(file)
                except Exception as e:
                    print(f"Error reading file {file.name}: {e}")
        if not stock_numbers:
            spinner.fail("No valid stock IDs found in 'input_stock' directory. Try running with option 2 to generate a template file.")
            sys.exit(1)
    elif choice == "2":
        template_file = input_dir / "stock_numbers.txt"
        with open(template_file, "w") as file:
            file.write("2303\n")
            file.write("2330\n")
        spinner.succeed(f"Template file created: {template_file}")
        sys.exit(0)
    elif choice == "3":
        spinner.succeed("Program exiting. . .")
        sys.exit(0)
    else:
        spinner.fail("Invalid choice. Exiting.")
        sys.exit(1)

    spinner.succeed("Stocks loaded successfully.")
    return stock_numbers


def main():
    # Check if all necessary folders exist
    check_all_folders()
    
    # Input for stock numbers and start date
    stock_numbers = get_stock_numbers()
    print(f"Total stock IDs loaded: {len(stock_numbers)}")
    print(stock_numbers)
    print("")
    
    # Step 0: Check if chromedriver is available
    spinner = Halo(text='Checking chromedriver...',
                   spinner='line', color='cyan')
    spinner.start()
    check_chromedriver()
    spinner.succeed("Chromedriver found.")
    print("")
    
    # Step 1: Run the download script with a spinner
    # check_and_download_stocks(stock_numbers)
    print("")
    
    # Step 2: Run the clean stocks script with a spinner
    spinner = Halo(text='Cleaning and processing data...',
                   spinner='line', color='cyan')
    spinner.start()
    try:
        processed_df = process_downloaded_stocks()
        spinner.succeed("Data cleaned and processed successfully.")
        print(processed_df)
    except Exception as e:
        spinner.fail(f"Failed to clean and process data: {e}")
        print(f"Exception during data cleaning and processing: {e}")
    print("")
    
    # Step 3: Run the MR backtest script with a spinner
    # spinner = Halo(text='Step 3: Performing MR backtesting...',
    #                spinner='line', color='cyan')
    # spinner.start()
    # try:
    #     # print("Calling process_stocks...")
    result_df = process_stocks()
    #     spinner.succeed("MR backtesting completed successfully.")
    print(result_df)
    # except Exception as e:
    #     spinner.fail(f"Failed to perform MR backtesting: {e}")
    #     print(f"Exception during MR backtesting: {e}")
    print("")
    
    spinner = Halo(text='..', spinner='none', color='cyan')
    spinner.start()
    spinner.succeed("Program completed successfully.")

if __name__ == "__main__":
    main()
