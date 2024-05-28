import asyncio
import json
from typing import Optional, Type

import jsonschema
from pydantic import BaseModel, Field, ValidationError

from .ada_enum import OperatingSystem
from .json_parser import JsonModelData, JsonParser
from .logger import logger
from .path_resolver import PathResolver


class FunctionManifestModel(BaseModel):
    """
        This is a data model for function's metadata json file.
    """
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$", title="Function Name")
    description: str = Field(..., title="Function Description")
    version: str = Field(..., pattern=r"^[0-9]+(\.[0-9]+)*$", title="Function Version")
    version_code: int = Field(..., gt=0, title="Function Version Code")
    target_version: str = Field(..., title="Function Target Version")
    target_version_code: int = Field(..., gt=0, title="Function Target Version Code")
    os_platform: list[OperatingSystem] = Field(..., title="Function OS Platform")
    entry: str = Field(..., title="Function Entry")
    in_params: Optional[str] = None
    out_results: Optional[str] = None
    callback: Optional[str] = None


class FunctionManifest(JsonModelData):
    """
        This class is to parse the manifest file of the function, including parameters and output results.
        These files are stored in the following directory structure:
        [name]@[version_code]
            |-----manifest.json
            |-----in_params.json  (optional)
            |-----out_results.json (optional)

        To access the value of 'name', use 'manifest_instance.model_instance.name'.

        'in_params.json' and 'out_results.json' are optional. If specified, they should be compliant to the
         json schema. See https://json-schema.apifox.cn/
    """
    MANIFEST_FILE_NAME = "manifest.json"

    def __init__(self, name_str: str, version_code: int, path_resolver: PathResolver = PathResolver()):
        super().__init__(FunctionManifestModel)

        self.function_name = name_str
        self.version_code = version_code
        self.func_id = FunctionManifest.generate_func_id(name_str, version_code)
        self.in_params_model_class = None
        self.out_results_model_class = None
        self.path_resolver = path_resolver

    @staticmethod
    def generate_func_id(func_name: str, version_code: int) -> str:
        # Generate the function id from function name and version code.
        return func_name + "@" + str(version_code)

    @staticmethod
    def split_func_id(func_id: str) -> tuple[bool, str, int]:
        # Split the function id into function name and version code.
        parts = func_id.split('@')
        if len(parts) != 2:
            logger.error(f"Invalid function id: {func_id}.")
            return False, "", 0
        version_code = 0
        try:
            version_code = int(parts[1])
        except ValueError as e:
            logger.error(f"Error to convert a string to int: {e}")
            return False, "", 0

        return True, parts[0], version_code

    async def parse_and_validate_from_file(self) -> bool:
        """
            Parse the manifest file from the file system. If any of in_params or out_results is specified,
            load and validate the json schema file, and finally load into the model class.
            :return: True if the manifest file is parsed successfully, otherwise False.
        """
        if self.model_instance is not None:
            logger.info(
                "The manifest file has been parsed. To parse again, please reset the model_instance to None.")
            return True

        json_parser = JsonParser()

        full_path = self.path_resolver.resolve_func_metadata_path(
            self.func_id, self.MANIFEST_FILE_NAME)
        if await json_parser.parse_json_file_to_dict(full_path) is None:
            return False

        # Model instance is stored in JsonModelData.model_instance if successfully parsed.
        return await self._internal_validate(json_parser)

    async def parse_and_validate_from_data(self, json_str: str) -> bool:
        """
            Parse the manifest file from the string data. If any of in_params or out_results is specified,
            load and validate the json schema file, and finally load into the model class.
            :return: True if the manifest file is parsed successfully, otherwise False.
        """
        if self.model_instance is not None:
            logger.info(
                "The manifest file has been parsed. To parse again, please reset the model_instance to None.")
            return True

        if not str:
            logger.error("Invalid JSON data.")
            return False

        json_parser = JsonParser()
        if json_parser.parse_json_str_to_dict(json_str) is None:
            return False

        return await self._internal_validate(json_parser)

    async def _internal_validate(self, json_parser: JsonParser) -> bool:
        # Not only do model validation, but also name and version code checks.
        if not json_parser.validate_dict_with_model(self):
            return False

        # Validate the values of the 2 keys.
        if self.model_instance.name != self.function_name:
            logger.error(
                f"Error：The name of the function is inconsistent with the name in the manifest file.")
            return False

        if self.model_instance.version_code != self.version_code:
            logger.error(
                f"Error：The version of the function is inconsistent with the version in the manifest file.")
            return False

        await self._generate_in_params_model()
        await self._generate_out_results_model()

        return True

    def validate_in_params_dict(self, json_dict: dict):
        # Validate the in_params json dict object and then return the model instance if correctly.
        # Return None if failed.
        try:
            return self.in_params_model_class(**json_dict)
        except ValidationError as e:
            logger.error(f"Failed to validate the in_params dict: {e}.")
            return None

    def validate_out_results_dict(self, json_dict: dict):
        # Validate the out_results json dict object and then return the model instance if correctly.
        # Return None if failed.
        try:
            return self.out_results_model_class(**json_dict)
        except ValidationError as e:
            logger.error(f"Failed to validate the out_results dict: {e}.")
            return None

    async def _generate_in_params_model(self):
        # Generate model class for further parameters' validation.
        if not self.model_instance.in_params:
            logger.info("'in_params' is not specified. No need to process it.")
            return

        full_path = self.path_resolver.resolve_func_metadata_path(
            self.func_id, self.model_instance.in_params)
        self.in_params_model_class = await self._parse_schema_file_to_model_class(full_path)

    async def _generate_out_results_model(self):
        # Generate model class for further results' validation.
        if not self.model_instance.out_results:
            logger.info("'out_results' is not specified. No need to process it.")
            return

        full_path = self.path_resolver.resolve_func_metadata_path(
            self.func_id, self.model_instance.out_results)
        self.out_results_model_class = await self._parse_schema_file_to_model_class(full_path)

    @staticmethod
    async def _parse_schema_file_to_model_class(full_path: str) -> Type[BaseModel] | None:
        parser = JsonParser()
        await parser.parse_json_file_to_dict(full_path)
        return parser.jsonschema_to_model_class()
