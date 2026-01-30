"""Configuration parsing and validation utilities.

This module provides functions to parse and validate configuration files for
maze generation, extracting and converting settings such as dimensions, entry/
exit coordinates, output file path, algorithm flags, and optional seed values.

Functions:
    is_all_mandatory: Check that all required keys exist in a config dict.
    return_config: Parse a config file and return validated settings.
"""

import sys
from typing import Any, Dict, Tuple


def is_all_mandatory(mandatory: Tuple, config: Dict[str, Any]) -> bool:
    """Checks whether all mandatory keys are in the configuration dictionary.

    Args:
        mandatory (Tuple): Tuple of mandatory keys.
        config (Dict[str, Any]): Configuration dictionary.

    Raises:
        ValueError: If a mandatory key is missing.

    Returns:
        bool: True if all mandatory keys are present.
    """
    for key in mandatory:
        if key not in config.keys():
            raise ValueError(f"You missing a mandatory {key} key!")
    return True


def return_config(input_file_name: str) -> Dict:
    """Parses the configuration file and returns a dictionary of
    maze generation settings.

    Args:
        input_file_name (str): Path of the config file.

    Raises:
        ValueError: If a key is invalid.
        ValueError: If the entry/exit coordinates are not valid.

    Returns:
        Dict: Configuration dictionary.
    """
    main_config: dict = {
        "WIDTH": int,
        "HEIGHT": int,
        "ENTRY": tuple,
        "EXIT": tuple,
        "OUTPUT_FILE": str,
        "PERFECT": bool,
        "SEED": int
    }
    config: dict = {}
    lines: list[str] = []
    with open(input_file_name, "r") as file:
        lines = [line.strip() for line in file if line.strip()]
        lines = [line for line in lines if not line.startswith("#")]
        if not lines:
            raise ValueError("File is empty!")

    for line in lines:
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in main_config:
            print(f"Error: {key} is not a valid key!", file=sys.stderr)
            sys.exit(1)

        try:
            if key in ("ENTRY", "EXIT"):
                tmp_tuple_value: list = value.split(",")
                if len(tmp_tuple_value) != 2:
                    raise ValueError(
                        "You must have exactly 2 coordinates!"
                    )
                config[key] = tuple(map(int, tmp_tuple_value))
            elif key == "PERFECT":
                val_lower: str = value.lower()

                if val_lower in ("true", "1"):
                    config[key] = True
                elif val_lower in ("false", "0"):
                    config[key] = False
            elif key and value:
                config[key] = main_config[key](value)
        except ValueError as e:
            print(f"Error processing {key}: {e}", file=sys.stderr)
            sys.exit(1)

    mandatory_keys = (
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT"
    )

    if is_all_mandatory(mandatory_keys, config):
        return config
    return {}
