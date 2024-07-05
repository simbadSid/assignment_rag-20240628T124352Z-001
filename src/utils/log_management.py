"""
log_management.py

This module contains functions for setting up and managing logging within the application.
It includes functionality to log messages to stdout and stderr with various levels of severity.
It may be adapted to log within a db or a format compatible with third-party log parsers.
"""

import logging
import sys
import traceback
from typing import Optional, Type

def setup_logger(stream=sys.stdout) -> logging.Logger:
    """
    Set up a logger.

    Args:
        stream: The stream to log to. Default is sys.stdout. Can be changed to a db manager or specific file.

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
    logger = setup_logger(stream=sys.stdout)
    log_func = getattr(logger, level.lower())
    log_func(message)

def log_error(message: str, exception_to_raise: Optional[Type[BaseException]] = None) -> None:
    """
    Log an error message to stderr. Designed to be changed to store complete logs in a dedicated structure (file, db),
    with the relevant information (time, process_id, call stack) and with a tunable granularity.

    Args:
        message (str): The error message to log.
        exception_to_raise (Optional[Type[BaseException]]): Exception class to raise after logging. Default is None.
    """
    logger = setup_logger(stream=sys.stderr)
    logger.error(message)
    traceback.print_exc(file=sys.stderr)

    if exception_to_raise:
        raise exception_to_raise(message)
