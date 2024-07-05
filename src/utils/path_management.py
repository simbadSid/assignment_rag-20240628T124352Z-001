"""
path_management.py

This module contains path and file management functions.
"""

import os

def project_root() -> str:
    """
    Get the absolute path to the project root directory.

    This function determines the root directory of the project by navigating up from the current file's directory.
    It is useful for constructing absolute paths to project files.

    Returns:
        str: Absolute path to the project root directory.
    """
    return os.path.abspath(os.path.join(__file__, '../../../'))

def path_to_absolute(file_relative_path: str) -> str:
    """
    Convert a relative file path to an absolute path based on the project root directory.

    This function takes a relative file path and converts it to an absolute path using the project root directory
    as the base. It is useful for ensuring that file paths are correctly resolved regardless of the current working directory.

    Args:
        file_relative_path (str): Relative path to a file.

    Returns:
        str: Absolute path to the file.
    """
    return os.path.join(project_root(), file_relative_path)
