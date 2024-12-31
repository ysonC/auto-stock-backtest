

# Stock Backtest Automation

This project automates the downloading, cleaning, and analysis of stock data to perform backtesting using Python. It provides modular scripts for different tasks like data extraction, cleaning, backtesting, and reporting.

## Installation

### 1. Set Up Python Environment

Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
![Venv](resources/venv.gif)
### 2. Run automated setup script

Run:
   ```bash
   pip install -e .
   ```
![Pip install](resources/pipinstall.gif)

## Manual Installation

### 1. Set Up Python Environment

Create a virtual environment for Python packages:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### 2. Update System and Install Dependencies

1. Update and upgrade your system:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```
2. Install required libraries:
   ```bash
   sudo apt install -y libnss3 libxss1 libappindicator3-1 libasound2
   ```

### 3. Install Google Chrome

1. Download and install Google Chrome:
   ```bash
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo dpkg -i google-chrome-stable_current_amd64.deb
   ```
2. Fix any broken dependencies:
   ```bash
   sudo apt --fix-broken install
   ```

### 4. Set Up ChromeDriver

1. Download ChromeDriver:  
   [ChromeDriver Download](https://googlechromelabs.github.io/chrome-for-testing/#stable)
2. Place the ChromeDriver file in the project directory and update the `chromedriver_path` in `download.py`:
   ```python
   # Update this path in download.py
   chromedriver_path = "/your-path/auto-stock-backtest/chromedriver"
   ```


## Usage

### Running the Main Script

To run the entire workflow, execute the main script:
   ```bash
   run
   ```
![run](resources/demo.gif)


## Features

- **Stock Data Download**: Automated downloading of stock data using Selenium and ChromeDriver.
- **Data Cleaning and Processing**: Extracts relevant metrics and performs validation.
- **Backtesting**: Median reversion success rate analysis based on historical stock data.
- **Logging**: Configurable logging for debugging and runtime analysis.
- **Modular Workflow**: Scripts can be executed independently or as part of a pipeline.


### Script Workflow

1. **Folder Setup**: Ensures required directories are available.
2. **Stock Data Input**: Reads stock IDs from the `input_stock/` directory.
3. **Data Download**: Fetches stock data from the web.
4. **Data Cleaning**: Extracts relevant metrics and processes data.
5. **Backtesting**: Performs median reversion analysis and generates reports.


### Key Configuration

Paths and constants can be adjusted in `config.py`.


## Files and Structure

- **`main.py`**: Entry point for the pipeline.
- **`download_stocks.py`**: Automates the stock data download process.
- **`clean_data.py`**: Cleans and validates downloaded stock data.
- **`backtest.py`**: Implements median reversion analysis.
- **`logging_config.py`**: Configures logging levels and formats.
- **`config.py`**: Central configuration for paths and constants.
- **`helpers.py`**: Utility functions for file operations and processing.
- **`download_chromedriver.py`**: Automates ChromeDriver setup.


## Notes

1. Ensure your `input_stock/stock_numbers.txt` file contains valid stock IDs.
2. Debug mode can be enabled by running scripts with the `debug` argument.
3. Logging output is available in `app.log`.

