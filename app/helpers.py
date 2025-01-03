import pandas as pd
from pathlib import Path
from halo import Halo
from datetime import datetime, timedelta
import logging
from .config import DATA_DIR, STOCK_DATA_DIR, RESOURCES_DIR, RESULTS_DIR, DOWNLOAD_DIR, INPUT_STOCK_DIR, LOGS_DIR

def read_excel(file_path, sheet_name=None):
    """Reads an Excel file into a pandas DataFrame."""
    try:
        if sheet_name:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def read_csv(file_path):
    """Reads a CSV file into a pandas DataFrame."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None


def save_to_excel(dataframe, file_path):
    """Saves a pandas DataFrame to an Excel file."""
    try:
        dataframe.to_excel(file_path, index=False)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving to Excel file: {e}")

def save_to_csv(dataframe, file_path, index=False):
    """
    Saves a pandas DataFrame to a CSV file.

    Args:
    - dataframe (pd.DataFrame): The DataFrame to save.
    - file_path (str or Path): The path to save the CSV file.
    - index (bool): Whether to include the DataFrame's index in the CSV. Default is False.
    - encoding (str): The encoding for the CSV file. Default is 'utf-8'.

    Returns:
    - None
    """
    try:
        file_path = Path(file_path)  # Ensure the file path is a Path object
        file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the parent directory exists
        
        dataframe.to_csv(file_path, index=index, encoding="utf-8")
        # print(f"Data successfully saved to {file_path.resolve()}")
    except Exception as e:
        print(f"Error saving CSV file to {file_path}: {e}")


def create_folder(folder_path):
    """
    Ensures that a folder exists. If it doesn't exist, it creates the folder.

    Args:
    - folder_path (str or Path): The path to the folder to check or create.
    """
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    
def run_process(task, task_description, success_message, failure_message):
    """Runs a task with a spinner and handles success or failure."""
    spinner = Halo(text=task_description, spinner='line', color='cyan')
    spinner.start()
    try:
        result = task()
        spinner.succeed(success_message)
        return result
    except Exception as e:
        spinner.fail(failure_message)
        raise e
    
def check_all_folders():
    """Check if all necessary folders exist."""
    logging.info("Verifying required folders.")
    folders = [DATA_DIR, INPUT_STOCK_DIR, RESULTS_DIR,
               STOCK_DATA_DIR, DOWNLOAD_DIR, RESOURCES_DIR,
               LOGS_DIR]
    for folder in folders:
        create_folder(folder)

def parse_custom_date(custom_date):
    """
    Converts custom date format (e.g., 24W52) to the Friday of that week in standard YYYY-MM-DD format.
    """
    try:
        year = int("20" + custom_date[:2])  # Assumes year is 20XX
        week = int(custom_date[3:])  # Extract the week number

        # Get the Monday of the given ISO week
        monday_date = datetime.strptime(f"{year}-W{week}-1", "%G-W%V-%u")

        # Add 4 days to get Friday
        friday_date = monday_date + timedelta(days=4)

        return friday_date.date()
    except Exception as e:
        logging.warning(f"Error parsing date '{custom_date}': {e}")
        return None