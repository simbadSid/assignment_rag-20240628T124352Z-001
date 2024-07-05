"""
config_management.py

This module handles the loading and management of configuration files for the application.
WARNING: the variable CONFIG_PATH needs to be modified according to any changes in the path of the JSON config file.
"""

import json
import os
from typing import Optional

from utils.log_management import log, log_error
from utils.path_management import path_to_absolute

CONFIG_PATH = path_to_absolute("config/config.json")

def load_config() -> dict:
    """
    Load configuration from a file. Handle errors if the file is not found or the JSON is invalid.

    Returns:
        dict: Configuration dictionary.
    """
    try:
        with open(CONFIG_PATH) as config_file:
            res = json.load(config_file)
            res = paths_to_absolute(res)
            log("Configuration loaded successfully", "info")
            return res
    except FileNotFoundError:
        log_error(f"Configuration file not found: {CONFIG_PATH}", exception_to_raise=RuntimeError)
    except json.JSONDecodeError as e:
        log_error(f"Error decoding JSON from the configuration file: {e}", exception_to_raise=RuntimeError)
    except Exception as e:
        log_error(f"Unexpected error: {e}", exception_to_raise=RuntimeError)

def load_config_secret_key(config_key_id: str, config: Optional[dict] = None) -> str:
    """
    Retrieves the secret key from the file specified in the configuration.

    Args:
        config_key_id: the expected key in the JSON config file.
        config (Optional[dict]): Configuration dictionary. If not provided, the function will load the configuration.

    Returns:
        str: The specified key.

    Raises:
        ValueError: If there is an error in retrieving or reading the key.
        FileNotFoundError: If the file specified in the config file is not correct.
    """
    # Load the configuration
    if config is None:
        config = load_config()

    # Retrieve the path of the file containing the OpenAI API key
    key_path = config["paths"].get(config_key_id)
    if not key_path:
        message = f"The required '{config_key_id}' parameter is missing in the configuration file specified in {CONFIG_PATH}."
        log_error(message, exception_to_raise=ValueError)

    # Check if the file exists
    if not os.path.isfile(key_path):
        message = f"The key file specified in {CONFIG_PATH} was not found: {config_key_id}"
        log_error(message, exception_to_raise=FileNotFoundError)

    # Read the API key from the file
    with open(key_path, 'r') as file:
        api_key = file.read().strip()

    if not api_key:
        message = f"The {config_key_id} key file specified in {CONFIG_PATH} is empty: {key_path}"
        log_error(message, exception_to_raise=ValueError)

    log(f"{config_key_id} key retrieved successfully from file: {key_path}", "info")
    return api_key

def paths_to_absolute(config: dict) -> dict:
    """
    Convert relative paths in the configuration to absolute paths based on the project root directory.

    Args:
        config (dict): Configuration dictionary containing relative paths.

    Returns:
        dict: Configuration dictionary with absolute paths.

    Raises:
        ValueError: If the 'paths' section in the configuration is missing or not a dictionary.
    """
    config_paths = config['paths']
    if not config_paths or not isinstance(config_paths, dict):
        message = f"The configuration file specified in {CONFIG_PATH} has errors in the 'paths' section."
        log_error(message, exception_to_raise=ValueError)

    for key, path in config_paths.items():
        config_paths[key] = path_to_absolute(path)

    return config
