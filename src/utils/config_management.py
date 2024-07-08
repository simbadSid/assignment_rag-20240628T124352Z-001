"""
config_management.py

This module handles the loading and management of configuration files for the application.
WARNING: the variable CONFIG_PATH needs to be modified according to any changes in the path of the JSON config file.
"""

import json
import os
from typing import Union, List

from utils.log_management import log, log_error
from utils.path_management import path_to_absolute

CONFIG_PATH = path_to_absolute("config/config.json")

class Config:
    def __init__(self):
        """
        Load configuration from a JSON config file. Handle errors if the file is not found or the JSON is invalid.
        """
        self.config_dict : dict = {}

        try:
            with open(CONFIG_PATH, 'r') as config_file:
                res = json.load(config_file)
                self.config_dict =  res
                log("Configuration loaded successfully", "info")
                self.paths_to_absolute()
        except FileNotFoundError:
            log_error(f"Configuration file not found: {CONFIG_PATH}", exception_to_raise=RuntimeError)
        except json.JSONDecodeError as e:
            log_error(f"Error decoding JSON from the configuration file: {e}", exception_to_raise=RuntimeError)
        except Exception as e:
            log_error(f"Unexpected error: {e}", exception_to_raise=RuntimeError)

    def load_config(self, key_to_search: Union[str, List[str]]) -> Union[str, dict]:
        """
                Load configuration value based on the key or nested keys provided.

                Args:
                    key_to_search (Union[str, List[str]]): Key or nested keys used to retrieve the configuration value.

                Returns:
                    Union[str, dict]: The value from the configuration corresponding to the key.

                Raises:
                    ValueError: If the specified key or nested key path does not exist in the configuration.
                """
        if isinstance(key_to_search, str):
            key_hierarchy = [key_to_search]
        else:
            key_hierarchy = key_to_search

        def get_conf(_key_hierarchy: List[str], sub_config_dict: dict) -> Union[str, dict, None]:
            key = _key_hierarchy[0]
            if not key in sub_config_dict:
                return None
            if len(_key_hierarchy) == 1:
                return sub_config_dict[key]
            else:
                return get_conf(_key_hierarchy[1:], sub_config_dict[key])

        res = get_conf(key_hierarchy, self.config_dict)
        if res is None:
            message = f"The required '{key_hierarchy}' parameter is missing in the configuration file specified in {CONFIG_PATH}."
            log_error(message, exception_to_raise=ValueError)

        return res

    def load_config_secret_key(self, config_id_key: str) -> str:
        """
        Retrieves the secret key from the file specified in the configuration.

        Args:
            config_id_key: the expected key in the JSON config file.

        Returns:
            str: The specified key.

        Raises:
            ValueError: If there is an error in retrieving or reading the key.
            FileNotFoundError: If the file specified in the config file is not correct.
        """

        # Retrieve the path of the file containing the OpenAI API key
        key_path = self.load_config(["paths", config_id_key])

        # Check the existence if the file containing the key
        if not os.path.isfile(key_path):
            message = f"The key file specified in {CONFIG_PATH} was not found: {config_id_key}"
            log_error(message, exception_to_raise=FileNotFoundError)

        # Read the API key from the file
        with open(key_path, 'r') as file:
            key_value = file.read().strip()

        if not key_value:
            message = f"The {config_id_key} key file specified in {CONFIG_PATH} is empty: {key_path}"
            log_error(message, exception_to_raise=ValueError)

        log(f"{config_id_key} key retrieved successfully from file: {key_path}", "info")
        return key_value

    def paths_to_absolute(self):
        """
        Convert relative paths in the configuration to absolute paths based on the project root directory.

        Raises:
            ValueError: If the 'paths' section in the configuration is missing or not a dictionary.
        """
        log(f"Setting the paths in the config file {CONFIG_PATH} to absolute paths", "info")

        config_paths = self.load_config('paths')
        if not config_paths or not isinstance(config_paths, dict):
            message = f"The configuration file specified in {CONFIG_PATH} has errors in the 'paths' section."
            log_error(message, exception_to_raise=ValueError)

        for key, path in config_paths.items():
            config_paths[key] = path_to_absolute(path)
