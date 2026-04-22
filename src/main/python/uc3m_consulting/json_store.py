"""JSON storage helpers."""
import json

from uc3m_consulting.enterprise_management_exception import (
    EnterpriseManagementException,
)


class JsonStore:
    """Persist JSON data."""

    @staticmethod
    def load_with_empty_default(file_path):
        """Load JSON data or return an empty list."""
        try:
            with open(file_path, "r", encoding="utf-8", newline="") as file:
                loaded_data = json.load(file)
        except FileNotFoundError:
            loaded_data = []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException(
                "JSON Decode Error - Wrong JSON Format"
            ) from ex
        return loaded_data

    @staticmethod
    def load_required(file_path):
        """Load a required JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8", newline="") as file:
                loaded_data = json.load(file)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException(
                "Wrong file  or file path"
            ) from ex
        return loaded_data

    @staticmethod
    def save(file_path, data_to_store):
        """Save data into a JSON file."""
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                json.dump(data_to_store, file, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException(
                "Wrong file  or file path"
            ) from ex
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException(
                "JSON Decode Error - Wrong JSON Format"
            ) from ex