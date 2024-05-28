import asyncio
import json
from io import UnsupportedOperation
from typing import Type

from jsonschema import Draft7Validator, SchemaError
from jsonschema_pydantic import jsonschema_to_pydantic
from pydantic import BaseModel, ValidationError, create_model

from .logger import logger


class JsonModelData:
    def __init__(self, model_class: Type[BaseModel]):
        # The model class is used to validate the parsed JSON data.
        self.model_class = model_class
        # The model instance is used to access the validated data.
        self.model_instance: model_class | None = None


class JsonParser:
    # A simple JSON parser wrapper class, for json file parsing, data model validation.
    # Typical usage:
    #     >>> parser = JsonParser()
    #     >>> result = parser.parse_json_file_to_dict(full_path)
    #     >>> parser.validate_dict_with_model(model_data)
    #     >>> print(model_data.model_instance.field1)
    def __init__(self):
        # Raw JSON string reading from file or from a memory-based string.
        self.json_str: str | None = None
        # Dict object parsed from json_data
        self.json_dict: dict | None = None

    async def parse_json_file_to_dict(self, full_path: str) -> dict | None:
        try:
            with open(full_path, "r") as f:
                self.json_str = f.read()
                logger.debug(f"JSON file read successfully for {full_path}.")
                return self._load_data_to_dict()
        except FileNotFoundError:
            logger.error(f"JSON file not found for {full_path}.")
            return None
        except PermissionError:
            logger.error(f"Permission denied for {full_path}.")
            return None
        except IsADirectoryError:
            logger.error(f"{full_path} is a directory.")
            return None
        except UnsupportedOperation:
            logger.error(f"Unsupported operation for {full_path}.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}.")
            return None

    def parse_json_str_to_dict(self, json_str: str) -> dict | None:
        # Parse data from a json string.
        if not json_str:
            logger.error("Invalid JSON data.")
            return None

        self.json_str = json_str
        return self._load_data_to_dict()

    def load_json_obj_to_dict(self, json_dict: dict) -> bool:
        # Load json data from a dict object.
        if not json_dict:
            logger.error("Invalid JSON object.")
            return False

        self.json_dict = json_dict
        return True

    def _load_data_to_dict(self) -> dict | None:
        # Don't call this directly. Call parse_json_file_to_dict or parse_json_data_to_dict instead.
        try:
            self.json_dict = json.loads(self.json_str)
            return self.json_dict
        except json.JSONDecodeError:
            logger.error("Invalid JSON format. Unable to parse JSON data.")
            return None

    def validate_dict_with_model(self, model_data: JsonModelData) -> bool:
        # Validate the dict object of json according to the given data model
        # and save the generated instance to model_data.model_instance.
        # Before calling this method, please make sure self.json_dict is generated or set.
        if self.json_dict is None:
            logger.error("Please parse json string to a dict firstly.")
            return False

        try:
            model_data.model_instance = model_data.model_class(**self.json_dict)
            return True
        except ValidationError as e:
            logger.error(e.json())
            return False

    def jsonschema_to_model_class(self) -> Type[BaseModel] | None:
        """
            This function should be called only when the json file or string is
            json schema compliant so that the file or string can be converted
            to a dynamical subclass of BaseModel.
            :return: A subclass info successfully. None when no dict is provided,
            or it's not a json schema string.
        """
        if self.json_dict is None:
            logger.error("Please parse json string to a dict firstly.")
            return None

        try:
            # jsonschema.validate(instance={}, schema=self.json_dict)
            Draft7Validator.check_schema(self.json_dict)
        except SchemaError as e:
            logger.error(f"Failed to validate the json dict compliant to json schema: {e}.")
            return None

        return jsonschema_to_pydantic(self.json_dict)
