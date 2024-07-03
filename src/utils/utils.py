import json
import logging
import sys
import traceback
from typing import Optional, Type

CONFIG_PATH = "config/config.json"

def load_config() -> dict:
    """
    Load configuration from a file. Handle errors if the file is not found.

    Returns:
        dict: Configuration dictionary.
    """
    try:
        with open(CONFIG_PATH) as config_file:
            return json.load(config_file)
    except FileNotFoundError as e:
        log_error(f"Configuration file not found: {CONFIG_PATH}", exception_to_raise=RuntimeError)
    except json.JSONDecodeError as e:
        log_error(f"Error decoding JSON from the configuration file: {e}", exception_to_raise=RuntimeError)
    except Exception as e:
        log_error(f"Unexpected error: {e}", exception_to_raise=RuntimeError)

def setup_logger(level: str = 'info', stream=sys.stdout) -> logging.Logger:
    """
    Set up a logger.

    Args:
        level (str): The log level ('info', 'debug', 'warning', 'error', 'critical'). Default is 'info'.
        stream: The stream to log to. Default is sys.stdout.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

def log(message: str, level: str = 'info') -> None:
    """
    Log a message to stdout. Designed to be changed to store complete logs in a dedicated structure (file, db),
    with the relevant information (time, process_id, call stack) and with a tunable granularity.

    Args:
        message (str): The message to log.
        level (str): The log level ('info', 'debug', 'warning', 'error', 'critical'). Default is 'info'.
    """
    logger = setup_logger(level='info', stream=sys.stdout)
    log_func = getattr(logger, level.lower(), 'info')
    log_func(message)

def log_error(message: str, exception_to_raise: Optional[Type[BaseException]] = None) -> None:
    """
    Log an error message to stderr. Designed to be changed to store complete logs in a dedicated structure (file, db),
    with the relevant information (time, process_id, call stack) and with a tunable granularity.

    Args:
        message (str): The error message to log.
        exception_to_raise (Optional[Type[BaseException]]): Exception class to raise after logging. Default is None.
    """
    logger = setup_logger(level='error', stream=sys.stderr)
    logger.error(message)
    traceback.print_exc(file=sys.stderr)

    if exception_to_raise:
        raise exception_to_raise(message)
