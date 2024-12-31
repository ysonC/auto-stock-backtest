import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file="app.log", level=logging.WARNING):
    """
    Configure logging for the application.

    Args:
    - log_file (str): Path to the log file.
    - level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
    """
    # Define the log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"

    # Create a rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    # Configure the root logger
    logging.basicConfig(
        level=level,
        handlers=[file_handler, console_handler]
    )

    logging.info("Logging is set up successfully.")
