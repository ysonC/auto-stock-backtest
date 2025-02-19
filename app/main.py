import sys
from pathlib import Path
from halo import Halo
import logging
from app import (
    read_stock_numbers_from_file,
    check_and_download_stocks,
    clean_downloaded_stocks,
    download_data,
    process_stocks,
    check_all_folders,
    setup_logging,
    log_separator,
    INPUT_STOCK_DIR
)


def get_stock_numbers():
    """Get stock numbers either manually or by reading all files in the 'input_stock' directory."""
    logging.info("Retrieving stock numbers.")

    print("Choose input method for stock numbers:")
    print("1. Load all stock IDs and date from files in 'input_stock' directory")
    print("2. Generate a template file in 'input_stock' directory")
    print("3. Exit")
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    print("")

    spinner = Halo(text='Loading stock IDs...', spinner='line', color='cyan')
    spinner.start()

    if choice == "1":
        stock_numbers = []
        for file in INPUT_STOCK_DIR.iterdir():
            if file.is_file():
                try:
                    with open(file, "r") as f:
                        stock_numbers = read_stock_numbers_from_file(file)
                        logging.info(
                            f"Loaded stock numbers from {file.name}: {stock_numbers}")
                except Exception as e:
                    logging.error(f"Error reading file {file.name}: {e}")
        if not stock_numbers:
            spinner.fail("No valid stock IDs found.")
            logging.error("No stock IDs found in 'input_stock' directory.")
            sys.exit(1)
    elif choice == "2":
        template_file = INPUT_STOCK_DIR / "stock_numbers.txt"
        with open(template_file, "w") as file:
            file.write("2303\n")
            file.write("2330\n")
        spinner.succeed(f"Template file created at {template_file}")
        logging.info(f"Template file created: {template_file}")
        sys.exit(0)
    elif choice == "3":
        spinner.succeed("Exiting program.")
        logging.info("Program exited by user.")
        sys.exit(0)
    else:
        spinner.fail("Invalid choice.")
        logging.error("Invalid choice entered. Exiting program.")
        sys.exit(1)

    spinner.succeed("Stock numbers loaded successfully.")
    logging.info(f"Loaded stock numbers: {len(stock_numbers)}")
    return stock_numbers


def main():
    debug_mode = len(sys.argv) > 1 and sys.argv[1] == "debug"
    setup_logging(debug_mode=debug_mode)
    check_all_folders()
    log_separator()
    if debug_mode:
        logging.info(
            "Debug mode enabled. All logs will be displayed in the terminal.")

    logging.info("Starting the application.")

    # Step 1: Get stock numbers
    stock_numbers = get_stock_numbers()
    print(f"Total stock IDs loaded: {len(stock_numbers)}")
    if len(stock_numbers) <= 10:
        print(stock_numbers)

    # Step 2: Check if chromedriver is available
    spinner = Halo(text='Checking ChromeDriver...',
                   spinner='line', color='cyan')
    spinner.start()
    spinner.succeed("ChromeDriver is available.")

    # Step 3: Download stock data
    logging.info("Starting stock data download.")
    print("1. To download stock data from Goodinfo, press 1.")
    print("2. To download shareholder data from Goodinfo, press 2.")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        check_and_download_stocks(stock_numbers)

    elif choice == "2":
        download_data(stock_numbers, "shareholder")

    logging.info("Stock data download completed.")

    # Step 4: Clean stock data
    spinner = Halo(text='Cleaning and processing data...',
                   spinner='line', color='cyan')
    spinner.start()
    try:
        processed_df = clean_downloaded_stocks(stock_numbers)
        spinner.succeed("Data cleaned and processed successfully.")
        print(processed_df)
        logging.info("Data cleaning and processing completed.")
    except Exception as e:
        spinner.fail(f"Error cleaning data: {e}")
        logging.error(f"Error during data cleaning: {e}")
        sys.exit(1)

    # Step 5: Perform MR backtesting
    spinner = Halo(text='Performing MR backtesting...',
                   spinner='line', color='cyan')
    spinner.start()
    try:
        result_df = process_stocks(stock_numbers)
        spinner.succeed("Backtesting completed.")
        print(result_df)
        logging.info("Backtesting completed successfully.")
    except Exception as e:
        spinner.fail(f"Error in backtesting: {e}")
        logging.error(f"Error during backtesting: {e}")
        sys.exit(1)

    logging.info("Program completed successfully.")
    print("Process finished.")


if __name__ == "__main__":
    logging.info("Program execution started.")
    try:
        main()
    except Exception as e:
        logging.critical(
            f"Unhandled exception in the program: {e}", exc_info=True)
