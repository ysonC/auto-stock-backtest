import os
import subprocess
import sys
import platform
import shutil
from tempfile import TemporaryDirectory

def run_command(command, description=None):
    """Run a system command and print its output."""
    if description:
        print(f"\n{description}...")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
        sys.exit(result.returncode)
    else:
        print(result.stdout.strip())

def setup_environment():
    """Set up the Python environment and dependencies."""
    print("\nSetting up Python environment...")

    # Create and activate virtual environment and install requirements
    print("Creating venv environment...")
    venv_cmd = "python3 -m venv .venv"
    run_command(venv_cmd, "Creating virtual environment and installing Python dependencies")
    
    # Update system and install required libraries
    print("\nUpdating system and installing required libraries...")
        # Update system and install required libraries
    if platform.system() == "Linux":
        run_command("sudo apt update && sudo apt upgrade -y", "Updating system")
        run_command("sudo apt install -y libnss3 libxss1 libappindicator3-1 libasound2", "Installing required libraries")
    elif platform.system() == "Darwin":
        run_command("brew update", "Updating Homebrew")
        # run_command("brew install wget libnss", "Installing required libraries")

def install_chrome_and_chromedriver(temp_dir):
    """Install Google Chrome and ChromeDriver."""
    print("\nInstalling Google Chrome...")

    # ChromeDriver setup
    print("\nSetting up ChromeDriver...")
    os_name = platform.system()
    if os_name == "Linux":
        os_key = "linux64"
    elif os_name == "Darwin":
        os_key = "mac-x64" if platform.machine() == "x86_64" else "mac-arm64"
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

    print(f"Detected OS: {os_name}")
    print("Downloading ChromeDriver...")
    download_link = f"https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/{os_key}/chromedriver-{os_key}.zip"
    chromedriver_zip = os.path.join(temp_dir, f"chromedriver-{os_key}.zip")
    run_command(f"wget {download_link} -O {chromedriver_zip}", "Downloading ChromeDriver")

    print("Unzipping ChromeDriver...")
    run_command(f"unzip {chromedriver_zip} -d {temp_dir}", "Extracting ChromeDriver")

    print("Moving ChromeDriver to current directory...")
    chromedriver_extracted = os.path.join(temp_dir, f"chromedriver-{os_key}", "chromedriver")
    shutil.move(chromedriver_extracted, "./setup/chromedriver")

    print("Cleaning up ChromeDriver zip and temp files...")
    os.remove(chromedriver_zip)
    shutil.rmtree(os.path.join(temp_dir, f"chromedriver-{os_key}"))

def download_chromedriver():
    # Check system compatibility
    os_name = platform.system()
    if os_name not in ["Linux", "Darwin"]:
        print("This script is designed for Linux or macOS-based systems.")
        sys.exit(1)

    # Create a temporary directory for downloads
    with TemporaryDirectory() as temp_dir:
        print(f"Temporary directory created: {temp_dir}")

        # Step 1: Set up Python environment
        # setup_environment()

        # Step 2: Install Chrome and ChromeDriver
        install_chrome_and_chromedriver(temp_dir)

        # Temporary directory and its contents are automatically deleted here
        print(f"Temporary directory {temp_dir} deleted.")
    print("")

if __name__ == "__main__":
    download_chromedriver()