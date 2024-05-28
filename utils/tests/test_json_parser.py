import asyncio
import json
import os
import sys
import unittest
from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel, Field

from utils.ada_enum import OperatingSystem
from utils.json_parser import JsonModelData, JsonParser
from utils.logger import logger


class TestJsonParser(unittest.TestCase):
    METADATA_DIR = "utils/tests/test_data/"

    class TestModel(BaseModel):
        field1: str = Field(..., title="Field 1")
        field2: int = Field(..., title="Field 2")
        field3: list = Field(..., title="Field 3")
        field4: dict = Dict[Literal["key1", "key2", "key3"], Union[int, str]]
        field5: Optional[str] = None

    JSON_STR = """
        {
            "field1": "value1",
            "field2": 2,
            "field3": [
                "value3",
                "value4"
            ],
            "field4": {
                "key1": 3,
                "key2": "4"
            }
        }
    """

    JSON_SCHEMA_STR = """
        {
            "type": "object",
            "properties": {
                "street_address": {
                    "type": "stringx"
                }
            },
            "required": ["name"]
        }
    """

    def test_json_load_file_correctly(self):
        model_data = JsonModelData(TestJsonParser.TestModel)
        parser = JsonParser()
        result = asyncio.run(parser.parse_json_file_to_dict(
            self.METADATA_DIR + "test_json_parser.json"))
        self.assertIsNotNone(result, "The json file should be loaded correctly.")

    def test_json_parsing_correctly(self):
        model_data = JsonModelData(TestJsonParser.TestModel)
        parser = JsonParser()
        result = parser.parse_json_str_to_dict(self.JSON_STR)
        self.assertIsNotNone(result, "The json data should be parsed correctly.")

    def test_json_parsing_with_errors(self):
        json_str = self.JSON_STR.replace('"value1"', '"value1", "value2"')
        model_data = JsonModelData(TestJsonParser.TestModel)
        parser = JsonParser()
        result = parser.parse_json_str_to_dict(json_str)
        self.assertIsNone(result, "The json data should be parsed with errors.")

    def test_json_validation(self):
        model_data = JsonModelData(TestJsonParser.TestModel)
        parser = JsonParser()
        result = parser.parse_json_str_to_dict(self.JSON_STR)
        self.assertIsNotNone(result, "The json data should be parsed correctly.")
        self.assertTrue(parser.validate_dict_with_model(model_data),
                        "The json data should be validated correctly.")
        self.assertIsNone(model_data.model_instance.field5, "The field5 should be None.")

        parser2 = JsonParser()
        json_str = self.JSON_STR.replace("field2", "fffddd")
        result = parser2.parse_json_str_to_dict(json_str)
        self.assertIsNotNone(result, "The json data should be parsed correctly.")
        self.assertFalse(parser2.validate_dict_with_model(model_data),
                         "The json data should be validated with errors.")

    def test_json_schema_validation(self):
        parser = JsonParser()
        result = asyncio.run(parser.parse_json_file_to_dict(
            self.METADATA_DIR + "json_schema_example.json"))
        self.assertIsNotNone(result, "The json file should be loaded correctly.")

        result = parser.jsonschema_to_model_class()
        self.assertIsNotNone(
            result, "The json schema file should be converted to a model class correctly.")

        parser2 = JsonParser()
        result2 = asyncio.run(parser2.parse_json_file_to_dict(
            self.METADATA_DIR + "json_example_data.json"))
        model_data = JsonModelData(result)
        self.assertTrue(parser2.validate_dict_with_model(model_data))
        self.assertEqual(model_data.model_instance.street_address, "1600 Pennsylvania Avenue NW")
        self.assertEqual(model_data.model_instance.country, "United States of America")

    def test_invalid_json_schema(self):
        # Only types, values of given keys are checked.
        # Any other keys in a json schema file or string will be ignored and no error will be reported.
        parser = JsonParser()
        result = parser.parse_json_str_to_dict(self.JSON_SCHEMA_STR)
        self.assertIsNone(parser.jsonschema_to_model_class(),
                          "The json schema file should be invalid.")


if __name__ == '__main__':
    unittest.main()
