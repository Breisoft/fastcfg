"""
This module defines the ConfigInterface class, which handles environment-specific configurations
and provides additional methods and attributes that are not directly related to configuration values.

Classes:
    ConfigInterface: Manages configuration attributes and environment settings.
"""

from fastcfg.config.base import AbstractConfigUnit
from fastcfg.config.utils import potentially_has_children
from fastcfg.validation.validatable import ValidatableMixin


class ConfigInterface(ValidatableMixin, AbstractConfigUnit):
    """
    Handles environment-specific configurations and provides additional public methods and attributes
    that are not directly related to configuration values, nor are meant to be overriden by config attributes.
    This separation allows the Config class to have public functions and variables without
    cluttering the main configuration logic.

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

    def update(self, **kwargs) -> "ConfigInterface":
        """
        Updates the configuration attributes. Adds or updates each key-value pair as an attribute.

        Args:
            **kwargs: Additional keyword arguments.
        """

        for key, value in kwargs.items():
            self._config_attributes.add_or_update_attribute(key, value)

        # Allows for method chaining
        return self

    def set_environment(self, env: str | None) -> "ConfigInterface":
        """
        Sets the current environment.

        Args:
            env: The environment to set.

        Raises:
            ValueError: If the environment is invalid.
        """

        if self._config_attributes.has_attribute(env) or env is None:
            self._current_env = env
        else:
            raise ValueError(f"Invalid environment: {env}")

        self._current_env = env

        # Allows for method chaining
        return self

    def remove_environment(self) -> "ConfigInterface":
        """
        Removes the current environment.
        """
        self.set_environment(None)

        # Allows for method chaining
        return self

    @property
    def environment(self) -> str | None:
        """
        Gets the current environment.

        Returns:
            The current environment.
        """
        return self._current_env

    def _get_env_dict(self, only_has_children=False) -> dict:
        all_attrs = self._config_attributes.get_attributes()

        envs = {}

        for attr, val in all_attrs.items():

            if only_has_children:
                # Config or dict is a valid environment
                if potentially_has_children(val):
                    envs[attr] = val
            else:
                envs[attr] = val

        return envs

    @property
    def environments(self):
        """
        Gets the environments.

        Returns:
            The environments.
        """

        from fastcfg.config.cfg import Config

        envs = self._get_env_dict(only_has_children=True)

        return Config(**envs)

    def get_dict(self) -> dict:
        """
        Gets the configuration attributes as a dictionary.

        Returns:
            dict: The configuration attributes.
        """

        attrs = self._get_env_dict()

        if self._current_env:
            attrs = attrs[self._current_env]

        if not isinstance(attrs, dict):
            attrs = attrs.__dict__

        return attrs

    @property
    def value(self):
        """
        Gets the configuration attributes as a dictionary.
        Primarily used to get the value for validation.

        Returns:
            dict: The configuration attributes.
        """
        return self.get_dict()
