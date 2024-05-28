from configparser import ConfigParser
from .logger import logger

logger.basic_config()

class ConfigLoader:
    """
    A class for loading and retrieving configurations from a ini config file.
    Usage:
        # Import the ConfigLoader class
        # Create an instance of ConfigLoader
        config_loader = ConfigLoader()

        # Load the config file, or load file with constructor.
        config_file = "/path/to/config.ini"
        config_loader.load_config_file(config_file)

        # Get a configuration value
        section = "database"
        config_name = "host"
        default_val = "localhost"
        host = config_loader.get_config(section, config_name, default_val)
        print(f"Database host: {host}")
    """

    def __init__(self, cfg_file=None):
        """
        Initializes a ConfigLoader object.

        Args:
            cfg_file (str): The path to the config file. Defaults to None.
        """
        self.cp = ConfigParser()
        if cfg_file:
            self.load_config_file(cfg_file)

    def load_config_file(self, cfg_file) -> bool:
        """
        Loads the config file.

        Args:
            cfg_file (str): The path to the config file.

        Returns:
            bool: True if the config file is loaded successfully, False otherwise.
        """
        logger.debug(f"config file path={cfg_file}")
        try:
            with open(cfg_file) as f:
                self.cp.read_file(f)
        except Exception as e:
            logger.error(f"Failed to read config file: {e}")
            return False
        return True

    def get_config(self, section, config_name, default_val="") -> str:
        """
        Retrieves a configuration value from the config file.

        Args:
            section (str): The section name in the config file.
            config_name (str): The name of the configuration.
            default_val (str): The default value to return if the configuration is not found. Defaults to "".

        Returns:
            str: The value of the configuration.
        """
        config_val = default_val
        if section and config_name:
            try:
                config_val = self.cp.get(section, config_name, fallback=default_val)
                logger.info(f"Get section={section}, config={config_name}, value={config_val}")
            except Exception as e:
                logger.error(f"Failed to get string config: {e}")
        return config_val
