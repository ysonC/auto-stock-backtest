import os
import subprocess
import sys
import platform
import shutil
import logging
from tempfile import TemporaryDirectory
import logging
from .config import CHROMEDRIVER_PATH

def run_command(command, description=None):
    """Run a system command and log its output."""
    if description:
        logging.info(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode != 0:
            logging.error(f"Command failed: {command}")
            logging.error(f"Error: {result.stderr.strip()}")
            sys.exit(result.returncode)
        else:
            logging.info(f"Command succeeded: {command}")
            logging.debug(f"Output: {result.stdout.strip()}")
    except Exception as e:
        logging.critical(f"Exception while running command '{command}': {e}", exc_info=True)
        sys.exit(1)

def setup_environment():
    """Set up the Python environment and dependencies."""
    logging.info("Setting up Python environment...")

    # Create and activate virtual environment
    logging.info("Creating venv environment...")
    venv_cmd = "python3 -m venv .venv"
    run_command(venv_cmd, "Creating virtual environment")

    # Update system and install required libraries
    logging.info("Updating system and installing required libraries...")
    if platform.system() == "Linux":
        run_command("sudo apt update && sudo apt upgrade -y", "Updating system")
        run_command("sudo apt install -y libnss3 libxss1 libappindicator3-1 libasound2", "Installing required libraries")
    elif platform.system() == "Darwin":
        run_command("brew update", "Updating Homebrew")

def install_chrome_and_chromedriver(temp_dir):
    """Download and install ChromeDriver."""
    logging.info("Setting up ChromeDriver...")
    os_name = platform.system()
    if os_name == "Linux":
        os_key = "linux64"
    elif os_name == "Darwin":
        os_key = "mac-x64" if platform.machine() == "x86_64" else "mac-arm64"
    else:
        logging.error(f"Unsupported OS: {os_name}")
        sys.exit(1)

    logging.info(f"Detected OS: {os_name}")
    logging.info("Downloading ChromeDriver...")
    download_link = f"https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/{os_key}/chromedriver-{os_key}.zip"
    chromedriver_zip = os.path.join(temp_dir, f"chromedriver-{os_key}.zip")
    run_command(f"wget {download_link} -O {chromedriver_zip}", "Downloading ChromeDriver")

    logging.info("Unzipping ChromeDriver...")
    run_command(f"unzip {chromedriver_zip} -d {temp_dir}", "Extracting ChromeDriver")

    logging.info("Moving ChromeDriver to current directory...")
    chromedriver_extracted = os.path.join(temp_dir, f"chromedriver-{os_key}", "chromedriver")
    try:
        shutil.move(chromedriver_extracted, "./resources/chromedriver")
        logging.info("ChromeDriver moved successfully.")
    except Exception as e:
        logging.error(f"Failed to move ChromeDriver: {e}", exc_info=True)
        sys.exit(1)

    logging.info("Cleaning up ChromeDriver zip and temp files...")
    try:
        os.remove(chromedriver_zip)
        shutil.rmtree(os.path.join(temp_dir, f"chromedriver-{os_key}"))
        logging.info("Temporary files cleaned up.")
    except Exception as e:
        logging.warning(f"Failed to clean up temporary files: {e}", exc_info=True)

def download_chromedriver():
    """Main function to download and set up ChromeDriver."""
    logging.info("Starting ChromeDriver setup...")

    os_name = platform.system()
    if os_name not in ["Linux", "Darwin"]:
        logging.error("This script is designed for Linux or macOS-based systems.")
        sys.exit(1)

    with TemporaryDirectory() as temp_dir:
        logging.info(f"Temporary directory created: {temp_dir}")

        # Set up environment
        # setup_environment()

        # Install ChromeDriver
        install_chrome_and_chromedriver(temp_dir)

        logging.info(f"Temporary directory {temp_dir} deleted automatically.")
    logging.info("ChromeDriver setup completed successfully.")

def check_chromedriver():
    """Check if ChromeDriver is installed and accessible."""
    if not CHROMEDRIVER_PATH.exists():
        logging.warning("ChromeDriver not found. Installing...")
        download_chromedriver()
        logging.info("ChromeDriver installed successfully.")
    else:
        logging.info("ChromeDriver is available.")

if __name__ == "__main__":
    logging.info("Script execution started.")
    try:
        download_chromedriver()
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True)
    logging.info("Script execution finished.")
