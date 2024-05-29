from fastcfg.config.items import IConfigItem
from fastcfg.validation.validatable import ValidatableMixin


class ConfigInterface(ValidatableMixin):
    """
    Designed to handle environment-specific configurations and provide additional methods and attributes that are not directly related to configuration values. 
    This separation allows the Config class to have public functions and variables without cluttering the main configuration logic.    
    """

    def __init__(self, config_attributes, **kwargs):

        super().__init__()

        self._config_attributes = config_attributes
        self._current_env = None

    def set_environment(self, env):
        self._current_env = env

    def get_environment(self):
        return self._current_env

    def get_dict(self):
        return self._config_attributes.get_attributes()

    @property
    def value(self):
        return self.get_dict()
