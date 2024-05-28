import asyncio
import os
import sys
import unittest

from utils.ada_enum import OperatingSystem
from utils.function_metadata import FunctionManifest, FunctionManifestModel
from utils.logger import logger
from utils.path_resolver import PathResolver


class TestFunctionMetadata(unittest.TestCase):
    FUNCTION_NAME_ARRAY = [
        "ltd.loox.oneaction.createnote",
        "ltd.loox.oneaction.createnote",
        "ltd.loox.oneaction.deletenote"
    ]
    FUNCTION_VERSION_ARRAY = [
        1,
        2,
        2
    ]

    METADATA_DIR = "utils/tests/test_data"

    JSON_DATA_STR = """
        {
            "name": "ltd.loox.testing.test1",
            "description": "Create a new OneNote page.",
            "version": "1.1.0",
            "version_code": 23456,
            "target_version": "1.0.0",
            "target_version_code": 1,
            "os_platform": [
                "Windows",
                "Linux_Cloud"
            ],
            "entry": "createonenote.py",
            "in_params": "",
            "out_results": "", "callback": ""
        }
    """
    JSON_FUNCTION_NAME = "ltd.loox.testing.test1"
    JSON_FUNCTION_VERSION_CODE = 23456

    def setUp(self):
        PathResolver().set_func_meta_dir(self.METADATA_DIR)

    def test_with_correct_metadata(self):
        logger.debug(f"current dir = {os.getcwd()}")
        function_manifest = FunctionManifest(
            self.FUNCTION_NAME_ARRAY[0], self.FUNCTION_VERSION_ARRAY[0])
        result = asyncio.run(function_manifest.parse_and_validate_from_file())

        self.assertTrue(result, "The function metadata is not correctly loaded and parsed.")
        self.assertEqual(function_manifest.model_instance.name, self.FUNCTION_NAME_ARRAY[0],
                         "The function name is not correctly loaded and parsed.")
        self.assertEqual(function_manifest.model_instance.version_code,
                         self.FUNCTION_VERSION_ARRAY[0],
                         "The function version is not correctly loaded and parsed.")
        self.assertEqual(function_manifest.model_instance.description,
                         "This is a function for creating a note in oneaction app.",
                         "The function description is not correctly loaded and parsed.")
        self.assertEqual(function_manifest.model_instance.version, "1.0.0",
                         "The function version is not correctly loaded and parsed.")
        self.assertEqual(function_manifest.model_instance.target_version, "1.1.0",
                         "The function target version is not correctly loaded and parsed.")
        self.assertEqual(function_manifest.model_instance.target_version_code, 11,
                         "The function target version code is not correctly loaded and parsed.")

        self.assertEqual(function_manifest.model_instance.os_platform,
                         [OperatingSystem.ANDROID, OperatingSystem.ANDROID_CLOUD],
                         "The function os_platform is not correctly loaded and parsed.")

        # check entry
        self.assertEqual(function_manifest.model_instance.entry, "createnote_main.py",
                         "The function entry is not correctly loaded and parsed.")

        # check in_params
        self.assertEqual(function_manifest.model_instance.in_params, "parameters.json",
                         "The function in_params is not correctly loaded and parsed.")

        # check out_results
        self.assertEqual(function_manifest.model_instance.out_results, "results.json",
                         "The function out_results is not correctly loaded and parsed.")

        # check callback
        self.assertEqual(function_manifest.model_instance.callback, "",
                         "The function callback is not correctly loaded and parsed.")

    def test_with_optional_key(self):
        function_manifest = FunctionManifest(
            self.JSON_FUNCTION_NAME, self.JSON_FUNCTION_VERSION_CODE)
        tmp_json_str = self.JSON_DATA_STR.replace('"in_params": "",', '')
        result = asyncio.run(function_manifest.parse_and_validate_from_data(tmp_json_str))
        self.assertTrue(result, "The in_params is optional. Should be no errors.")

        tmp_json_str = self.JSON_DATA_STR.replace('"out_results": "",', '')
        result = asyncio.run(function_manifest.parse_and_validate_from_data(tmp_json_str))
        self.assertTrue(result, "The out_results is optional. Should be no errors.")

        tmp_json_str = self.JSON_DATA_STR.replace(', "callback": ""', '')
        result = asyncio.run(function_manifest.parse_and_validate_from_data(tmp_json_str))
        self.assertTrue(result, "The callback is optional. Should be no errors.")

    def test_with_versions_error(self):
        function_manifest = FunctionManifest(
            self.FUNCTION_NAME_ARRAY[1], self.FUNCTION_VERSION_ARRAY[1])
        result = asyncio.run(function_manifest.parse_and_validate_from_file())
        self.assertFalse(result, "The version error should be expected to report.")

    def test_with_version_code_type_error(self):
        function_manifest = FunctionManifest(
            self.FUNCTION_NAME_ARRAY[2], self.FUNCTION_VERSION_ARRAY[2])
        result = asyncio.run(function_manifest.parse_and_validate_from_file())
        self.assertFalse(result, "The version code type error should be expected to report.")

    def test_with_diff_type_errors(self):
        function_manifest = FunctionManifest(
            self.JSON_FUNCTION_NAME, self.JSON_FUNCTION_VERSION_CODE)
        result = asyncio.run(function_manifest.parse_and_validate_from_data(self.JSON_DATA_STR))
        self.assertTrue(result, "The function metadata is not correctly loaded and parsed.")

        function_manifest = FunctionManifest(
            self.JSON_FUNCTION_NAME, self.JSON_FUNCTION_VERSION_CODE)
        tmp_json_str = self.JSON_DATA_STR.replace("1.1.0", "1,1.0")
        result = asyncio.run(function_manifest.parse_and_validate_from_data(tmp_json_str))
        self.assertFalse(result, "The version error should be expected to report.")

        function_manifest = FunctionManifest(
            self.JSON_FUNCTION_NAME, self.JSON_FUNCTION_VERSION_CODE)
        tmp_json_str = self.JSON_DATA_STR.replace("23456", "-10")
        result = asyncio.run(function_manifest.parse_and_validate_from_data(tmp_json_str))
        self.assertFalse(result, "The version code error should be expected to report.")

        function_manifest = FunctionManifest(
            self.JSON_FUNCTION_NAME, self.JSON_FUNCTION_VERSION_CODE)
        tmp_json_str = self.JSON_DATA_STR.replace("Windows", "win")
        result = asyncio.run(function_manifest.parse_and_validate_from_data(tmp_json_str))
        self.assertFalse(result, "The os_platform error should be expected to report.")

    def test_generate_split_func_id(self):
        func_id = FunctionManifest.generate_func_id(self.JSON_FUNCTION_NAME, self.JSON_FUNCTION_VERSION_CODE)
        self.assertEqual(func_id, "ltd.loox.testing.test1@23456",
                         "The function id is not correctly generated.")

        result = FunctionManifest.split_func_id(func_id)
        self.assertTrue(result[0], "The function id is not correctly split.")
        self.assertEqual(result[1], self.JSON_FUNCTION_NAME, "The function name is not correctly split.")
        self.assertEqual(result[2], self.JSON_FUNCTION_VERSION_CODE,
                         "The function version code is not correctly split.")

        result = FunctionManifest.split_func_id("ltd.loox.testing.test1")
        self.assertFalse(result[0], "The function id is not correctly split.")


if __name__ == '__main__':
    unittest.main()
