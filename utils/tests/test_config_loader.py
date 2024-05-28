import unittest
from utils.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):

    def setUp(self):
        self.config_loader = ConfigLoader()

    def test_load_config_file(self):
        config_file = "utils/tests/test_config.ini"
        result = self.config_loader.load_config_file(config_file)
        self.assertTrue(result)

    def test_get_config(self):
        section = "config"
        config_name = "host"
        default_val = "localhost"
        expected_result = "example.com"
        self.config_loader.load_config_file("utils/tests/test_config.ini")
        result = self.config_loader.get_config(section, config_name, default_val)
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
