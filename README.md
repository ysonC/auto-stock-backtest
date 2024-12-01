
---

# Stock Backtest Automation

Automate the process of downloading, processing, and analyzing stock data to perform backtesting with Python scripts.

---

## Installation

### 0. Run automated setup script
1. Run:
   ```bash
   python3 setup.py
   ```

### 1. Set Up Python Environment
1. Create a virtual environment for Python packages:
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

---

## Usage

### Running the Main Script
To run the entire workflow, execute the main script:
```bash
python main.py
```

### Main Script Workflow
1. Downloads stock data (`download.py`).
2. Extracts the required data from downloaded files (`extract_data.py`).
3. Processes and analyzes the data (`process.py`).
4. Performs backtesting on the processed data (`backtest.py`).

### Running Scripts Independently
You can run each script independently:
- **Extract Data**: `extract_data.py`
- **Process Data**: `process.py`
- **Backtest**: `backtest.py`

---

### Notes

---
