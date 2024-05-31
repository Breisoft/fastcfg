from fastcfg.validation.validatable import ValidatableMixin


class ConfigInterface(ValidatableMixin):
    """
    Handles environment-specific configurations and provides additional methods and attributes
    that are not directly related to configuration values. This separation allows the Config class
    to have public functions and variables without cluttering the main configuration logic.

    Attributes:
        _config_attributes (ConfigAttributes): The configuration attributes.
        _current_env (str): The current environment.

    Methods:
        __init__(config_attributes, **kwargs): Initializes the `ConfigInterface` object.
        set_environment(env): Sets the current environment.
        get_environment(): Retrieves the current environment.
        get_dict(): Returns the configuration attributes as a dictionary.
        value: Property that gets the configuration attributes as a dictionary.
    """

    def __init__(self, config_attributes, **kwargs):
        """
        Initializes the ConfigInterface.

        Args:
            config_attributes: The configuration attributes.
            **kwargs: Additional keyword arguments.
        """
        super().__init__()
        self._config_attributes = config_attributes
        self._current_env = None

    def set_environment(self, env):
        """
        Sets the current environment.

        Args:
            env: The environment to set.
        """
        self._current_env = env

    def get_environment(self):
        """
        Gets the current environment.

        Returns:
            The current environment.
        """
        return self._current_env

    def get_dict(self):
        """
        Gets the configuration attributes as a dictionary.

        Returns:
            dict: The configuration attributes.
        """
        return self._config_attributes.get_attributes()

    @property
    def value(self):
        """
        Gets the configuration attributes as a dictionary.
        Primarily used to get the value for validation.

        Returns:
            dict: The configuration attributes.
        """
        return self.get_dict()
