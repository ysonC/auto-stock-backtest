import logging
from logging.handlers import RotatingFileHandler
from .config import LOGS_DIR

def setup_logging(log_file=LOGS_DIR / "app.log", file_level=logging.DEBUG, debug_mode=False):
    """
    Configure logging to log into a file and optionally display all logs in the terminal.

    Args:
    - log_file (str): Path to the log file.
    - file_level (int): Logging level for the file handler.
    - debug_mode (bool): If True, enable debug-level logs in the terminal.
    """
    # Define the log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    # Suppress Selenium logs
    selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
    selenium_logger.setLevel(logging.WARNING)  # Suppress DEBUG and INFO logs


    # File handler for detailed logging
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(file_level)

    # Configure logging handlers
    handlers = [file_handler]

    # Add console handler in debug mode
    if debug_mode:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        console_handler.setLevel(logging.DEBUG)
        handlers.append(console_handler)

    # Clear existing handlers
    logging.root.handlers.clear()

    # Set up logging with the configured handlers
    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
    
def log_separator():
    """
    Log a separator to mark the beginning of a new script execution.
    """
    logging.info("\n" + "-" * 80)

