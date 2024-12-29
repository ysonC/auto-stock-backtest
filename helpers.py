import pandas as pd

def read_excel(file_path, sheet_name=None):
    """
    Reads an Excel file into a pandas DataFrame.
    If sheet_name is provided, loads the specified sheet.
    """
    try:
        if sheet_name:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def read_csv(file_path):
    """
    Reads a CSV file into a pandas DataFrame.
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None
