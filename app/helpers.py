import pandas as pd
from pathlib import Path

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