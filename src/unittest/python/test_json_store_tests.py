"""Tests for json_store module."""
import json
import os
import tempfile
import unittest

from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.json_store import JsonStore


class TestJsonStore(unittest.TestCase):
    """Test cases for JsonStore."""

    def test_load_with_empty_default_when_file_does_not_exist(self):
        """It should return an empty list when the file does not exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = os.path.join(temp_dir, "missing.json")
            result = JsonStore.load_with_empty_default(missing_file)
            self.assertEqual([], result)

    def test_save_and_load_required(self):
        """It should save and load JSON content correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = os.path.join(temp_dir, "data.json")
            expected_data = [{"name": "project1"}, {"name": "project2"}]

            JsonStore.save(json_file, expected_data)
            loaded_data = JsonStore.load_required(json_file)

            self.assertEqual(expected_data, loaded_data)

    def test_load_required_when_file_does_not_exist(self):
        """It should raise an exception when a required file does not exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = os.path.join(temp_dir, "missing.json")

            with self.assertRaises(EnterpriseManagementException) as context:
                JsonStore.load_required(missing_file)

            self.assertEqual("Wrong file  or file path", context.exception.message)

    def test_load_with_empty_default_wrong_json_format(self):
        """It should raise an exception when JSON format is invalid."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = os.path.join(temp_dir, "broken.json")

            with open(json_file, "w", encoding="utf-8") as file:
                file.write("{broken json}")

            with self.assertRaises(EnterpriseManagementException) as context:
                JsonStore.load_with_empty_default(json_file)

            self.assertEqual(
                "JSON Decode Error - Wrong JSON Format",
                context.exception.message,
            )

    def test_save_then_verify_file_content(self):
        """It should write the expected content to disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = os.path.join(temp_dir, "written.json")
            expected_data = [{"id": 1, "value": "ok"}]

            JsonStore.save(json_file, expected_data)

            with open(json_file, "r", encoding="utf-8") as file:
                file_content = json.load(file)

            self.assertEqual(expected_data, file_content)


if __name__ == "__main__":
    unittest.main()
