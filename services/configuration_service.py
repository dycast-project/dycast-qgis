import os
import pickle
from dycast_qgis.models.configuration import Configuration

class ConfigurationService():
    def __init__(self, config_file_path=None):
        self.config_file_path = config_file_path or self._get_default_config_path()

    def _get_default_config_path(self):
        return os.path.join(self._get_root_directory(), "dycast_qgis.config")

    def _get_root_directory(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        return os.path.abspath(
            os.path.join(current_directory, ".."))

    def persist_config(self, config: Configuration):
        config_file = open(self.config_file_path, "wb")
        pickle.dump(config, config_file)
        config_file.close()

    def load_config(self):
        try:
            return pickle.load(open(self.config_file_path, "rb"))
        except (FileNotFoundError, EOFError, TypeError):
            return Configuration()
