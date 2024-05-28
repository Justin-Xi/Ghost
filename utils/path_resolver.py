from .logger import logger
from .singleton import singleton


@singleton
class PathResolver:
    """
        A singleton class to make sure it can be gotten everywhere.
        Explicitly set the base directory of function metadata and group chain template when changing
        the working directories for group chain template and function.
    """
    DEFAULT_FUNCTION_META_DIR = "./"
    DEFAULT_CHAIN_TEMPL_DIR = "./"

    def __init__(self):
        # func_meta_dir specifies the base directory for directories of all function metadata.
        self.func_meta_dir = "./"
        self.chain_templ_dir = "./"

    def set_func_meta_dir(self, meta_base_dir: str):
        if not str:
            logger.warning("Can't set an empty string as the base directory of function metadata.")
            return

        self.func_meta_dir = meta_base_dir

    def set_chain_templ_dir(self, templ_base_dir: str):
        if not str:
            logger.warning(
                "Can't set an empty string as the base directory of group chain template.")
            return
        self.chain_templ_dir = templ_base_dir

    def resolve_func_metadata_path(self, meta_func_id: str, meta_file_name) -> str:
        return self.func_meta_dir + "/" + meta_func_id + "/" + meta_file_name

    def resolve_group_template_path(self, template_file_name: str) -> str:
        return self.chain_templ_dir + "/" + template_file_name
