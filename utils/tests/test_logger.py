import logging
import os
import unittest
from logging import DEBUG, ERROR, INFO, WARNING

from utils.logger import logger


class TestLogger(unittest.TestCase):
    LOG_FILE = "utils/tests/utils_testlog.txt"

    def setUp(self):
        self.remove_log_file()
        self.reset_logging()
        logger.basic_config(WARNING, TestLogger.LOG_FILE)

    def tearDown(self):
        self.remove_log_file()
        self.reset_logging()

    def remove_log_file(self):
        if os.path.exists(self.LOG_FILE):
            os.remove(self.LOG_FILE)

    def reset_logging(self):
        # 移除所有现有的日志处理程序
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    @staticmethod
    def log_file_contains_message(message) -> bool:
        try:
            with open(TestLogger.LOG_FILE, "r") as f:
                return message in f.read()
        except Exception as e:
            return False

    def test_logger_append_to_file(self):
        logger.debug("debugging message")
        logger.warning("warning message")
        logger.info("info message")
        logger.error("error message")
        self.assertFalse(self.log_file_contains_message("debugging message"))
        self.assertTrue(self.log_file_contains_message("warning message"))
        self.assertFalse(self.log_file_contains_message("info message"))
        self.assertTrue(self.log_file_contains_message("error message"))


if __name__ == '__main__':
    unittest.main()
