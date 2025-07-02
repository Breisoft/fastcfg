"""
This module defines the ConfigInterface class, which handles environment-specific configurations
and provides additional methods and attributes that are not directly related to configuration values.

Classes:
    ConfigInterface: Manages configuration attributes and environment settings.
"""

from fastcfg.config.items import AbstractConfigItem
from fastcfg.config.base import AbstractConfigUnit
from fastcfg.config.utils import potentially_has_children, deep_merge_config
from fastcfg.validation.validatable import ValidatableMixin
from fastcfg.config.events import EventListenerMixin
import pickle

class ConfigInterface(ValidatableMixin, EventListenerMixin, AbstractConfigUnit):
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
        to_dict(): Returns the configuration attributes as a dictionary.
        value: Property that gets the configuration attributes as a dictionary.
    """

    def __init__(self, config, config_attributes, **kwargs):
        """
        Initializes the ConfigInterface.

        Args:
            config_attributes: The configuration attributes.
            **kwargs: Additional keyword arguments.
        """
        super().__init__()
        self._config = config
        self._parent = None
        self._config_attributes = config_attributes
        self._current_env = None

    def set_parent(self, parent: 'Config'):
        """Set the parent Config object."""

        self._parent = parent

    def update(self, other=None, **kwargs) -> "ConfigInterface":
        """
        Updates the configuration attributes using deep merge. Works like dict.update() but preserves nested values.
        
        Can accept either a dict-like object or keyword arguments.
        If an environment is currently active, updates will only affect that environment.
        Dictionaries are automatically converted to Config objects.

        Args:
            other: A dict-like object or iterable of key-value pairs.
            **kwargs: Additional keyword arguments.
        """
        # Determine the target for updates
        if self._current_env:
            target = getattr(self._config, self._current_env)
        else:
            target = self._config
        
        # Process the main data
        if other is not None:
            if hasattr(other, 'items'):
                # Handle dict-like objects
                deep_merge_config(target, other)
            else:
                # Handle sequence of pairs
                deep_merge_config(target, dict(other))
        
        # Handle keyword arguments
        if kwargs:
            deep_merge_config(target, kwargs)

        # Allows for method chaining
        return self
    
    def save(self, file_path: str):
        """
        Saves the full configuration state to a file.
        """
        with open(file_path, "wb") as f:
            pickle.dump(self._config, f)

    def load(self, file_path: str):
        """
        Loads the full configuration state from a file.
        """
        with open(file_path, "rb") as f:
            self._config = pickle.load(f)

    def export_values(self, file_path: str):
        """
        Exports the current configuration values to a file.
        """
        from fastcfg.util import save_file
        save_file(file_path, self._config.to_dict())

    def import_values(self, file_path: str):
        """
        Imports the current configuration values from a file using deep merge.
        
        If an environment is currently active, the import will only affect that environment.
        If no environment is active, the import will affect the root configuration.
        Existing nested values are preserved unless explicitly overwritten.
        """
        from fastcfg.util import load_file

        data = load_file(file_path)
        self.update(data)

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

    def to_dict(self) -> dict:
        """
        Gets the configuration attributes as a dictionary. Fully serializable.
        It will also resolve nested Config objects to their dictionary
        representation and ConfigItems as their value.

        Returns:
            dict: The configuration attributes.
        """
        from fastcfg.config.cfg import Config

        attrs = self._get_env_dict()

        # Recursively resolve nested Config objects and ConfigItems to their dictionary
        # representation and their value.
        for k, v in attrs.items():
            if isinstance(v, Config):
                attrs[k] = v.to_dict()
            elif isinstance(v, AbstractConfigItem):
                attrs[k] = v.value

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
        return self.to_dict()
    
    def keys(self):
        """
        Returns a view of the configuration's keys.
        """
        return self.to_dict().keys()
    
    def values(self):
        """
        Returns a view of the configuration's values.
        """
        return self.to_dict().values()
    
    def items(self):
        """
        Returns a view of the configuration's (key, value) pairs.
        """
        return self.to_dict().items()
    
    def get(self, key, default=None):
        """
        Get a configuration value with a default if the key doesn't exist.
        """
        try:
            return getattr(self._config, key)
        except AttributeError:
            return default
    
    def pop(self, key, *args):
        """
        Remove and return a configuration value.
        """
        if len(args) > 1:
            raise TypeError(f"pop expected at most 2 arguments, got {len(args) + 1}")
        
        try:
            value = getattr(self._config, key)
            delattr(self._config, key)
            return value
        except AttributeError:
            if args:
                return args[0]
            raise KeyError(key)
