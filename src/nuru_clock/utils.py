import logging
import os
from dotenv import load_dotenv
from colorama import Fore, Style


load_dotenv()

# Define log levels with colored tags
LOG_LEVELS = {
    "DEBUG": f"{Fore.BLUE}[DEBUG]{Style.RESET_ALL}",
    "INFO": f"{Fore.GREEN}[INFO]{Style.RESET_ALL}",
    "WARNING": f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL}",
    "ERROR": f"{Fore.RED}[ERROR]{Style.RESET_ALL}",
    "CRITICAL": f"{Fore.MAGENTA}[CRITICAL]{Style.RESET_ALL}",
}

# Get log file path from .env file
LOG_FILE = os.getenv("LOG_FILE", None)

# Create a custom logger
logger = logging.getLogger("nuru_clock_logger")

# Set the default log level (can be overridden by .env)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(LOG_LEVEL)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

# Create a file handler only if LOG_FILE is specified
file_handler = None
if LOG_FILE:
    try:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(LOG_LEVEL)
    except Exception as e:
        logger.warning(f"Failed to create file handler for logging: {e}")


# Define a custom formatter for colored logs
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level_name = record.levelname
        colored_tag = LOG_LEVELS.get(level_name, "")
        record.msg = f"{colored_tag} {record.msg}"
        return super().format(record)


formatter = ColoredFormatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(formatter)


if file_handler:
    file_handler.setFormatter(formatter)


# Add handlers to the logger
logger.addHandler(console_handler)
if file_handler:
    logger.addHandler(file_handler)


# Utility function to log messages
def log(level: str, message: str):
    """
    Logs a message with the specified level.

    :param level: Log level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    :param message: The message to log.
    """
    level = level.upper()
    if level == "DEBUG":
        logger.debug(message)
    elif level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "CRITICAL":
        logger.critical(message)
    else:
        logger.info(message)  # Default to INFO if level is invalid
