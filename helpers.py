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
        
def create_folder(folder_path):
    """
    Ensures that a folder exists. If it doesn't exist, it creates the folder.

    Args:
    - folder_path (str or Path): The path to the folder to check or create.
    """
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)