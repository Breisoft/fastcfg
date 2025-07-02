"""
This module provides the `Config` class for managing configuration settings in a structured and flexible manner.

The `Config` class is the primary basis for interacting with the `fastcfg` library. 

It supports:
    - Dynamic attribute management
    - Nested configurations
    - Validation mechanisms
    - Live-updating attributes that are fetched on attribute access.
    - Environment-specific configurations. 
    
It allows for easy setting, getting, and updating of configuration attributes, and ensures configuration integrity through optional validation.

Usage Example:

    ```python
    from fastcfg.config.cfg import Config

    # Initialize a configuration with nested dictionaries
    config = Config(database={'host': 'localhost', 'port': 5432})

    # Access nested configuration attributes with dot notation
    print(config.database.host) # Output: localhost

    # Add or update attributes dynamically
    config.new_attr = 'value'

    print(config.new_attr) # Output: value

    # Compare configuration with a dictionary
    assert config == {'database': {'host': 'localhost', 'port': 5432}, 'new_attr': 'value'}
    
    # Get string representation of the configuration
    print(str(config)) # Output: {'database': {'host': 'localhost', 'port': 5432}, 'new_attr': 'value'}
    ```

"""

from typing import Any

from fastcfg.config.base import AbstractConfigUnit
from fastcfg.config.attributes import ConfigAttributes
from fastcfg.config.interface import ConfigInterface
from fastcfg.config.items import AbstractConfigItem
from fastcfg.config.utils import create_config_dict
from fastcfg.config.value_wrapper import ValueWrapper

import pickle
import json

def _get_dict(config: "Config") -> dict:
    """
    Gets the dictionary representation of the Config object.
    """
    return config.__dict__["__interface"].to_dict()

def _chain_return_helper(config: "Config", return_obj: Any) -> Any:
    """
    This function is used to help with method chaining, i.e.:

    config.update(a=1).update(b=2).add_validator(lambda x: x > 0)

    This is because some functions on Config, ConfigInterface, and ConfigAttributes
    return the object itself, so we need to return the Config object
    in that case.

    AbstractConfigUnit is currently only used as a base to simplify this
    return process
    """
    # This is used to allow for method chaining on any Config-related
    # object
    # Some functions on Config, ConfigInterface, and ConfigAttributes
    # return the object itself, so we need to return the Config object
    # in that case.
    # AbstractConfigUnit is currently only used as a base to simplify this
    # return process

    # We always want to return Config itself to allow for broad attribute and
    # method access for chaining
    if isinstance(return_obj, AbstractConfigUnit):
        return config
    return return_obj


class Config(AbstractConfigUnit):
    """
    The `Config` class is designed to manage configuration settings in a structured and flexible manner.

    Features:
        - **Dynamic Attribute Management**: Allows dynamic setting and getting of attributes.
        - **Nested Configuration**: Supports nested dictionaries by converting them into `Config` objects.
        - **Validation**: Integrates with validation mechanisms to ensure configuration integrity.
        - **Environment-Specific Configurations**: Supports environment-specific configurations through the `ConfigInterface`.

    How it Works:
        - **Initialization**: Accepts keyword arguments to set initial configuration values.
        - **Attribute Setting**: Uses `__setattr__` to add or update attributes, converting dictionaries to `Config` objects.
        - **Attribute Getting**: Uses `__getattr__` and `__getattribute__` to retrieve attributes, supporting environment-specific lookups and wrapping values in `ValueWrapper`.
        - **Equality Check**: Compares the configuration with dictionaries by converting internal attributes to a dictionary.
        - **String Representation**: Provides a string representation of the configuration by converting it to a dictionary.

    Example:

    ```
    python
    config = Config(database={'host': 'localhost', 'port': 5432})
    print(config.database.host) # Output: localhost
    config.new_attr = 'value'
    print(config.new_attr) # Output: value
    ```

    Attributes:
        __attributes (ConfigAttributes): Manages the actual configuration values.
        __interface (ConfigInterface): Handles public-facing functions and attributes on behalf of the Config class.

    Methods:
        __init__(**kwargs): Initializes the configuration with given keyword arguments.
        __setattr__(name, value): Sets or updates an attribute.
        __getattr__(name): Retrieves an attribute, supporting environment-specific lookups.
        __getattribute__(name): Retrieves an attribute, wrapping values in `ValueWrapper` or returning a nested `Config` directly.
        __eq__(other): Compares the configuration with a dictionary.
        __str__(): Returns a string representation of the configuration.
    """

    @classmethod
    def load(cls, file_path: str) -> "Config":
        with open(file_path, "rb") as f:
            return pickle.load(f)

    def __init__(self, **kwargs):
        """
        Initializes the `Config` object with the given keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments representing initial configuration values.
                      If a value is a dictionary, it will be converted into a nested `Config` object.

        """

        attributes = ConfigAttributes(self)

        # Instead of directly setting attributes, we need to populate this instance's __dict__
        # object to avoid issues with setattr
        self.__dict__["__attributes"] = attributes
        self.__dict__["__interface"] = ConfigInterface(self, attributes)

        for k, v in kwargs.items():
            if isinstance(v, dict):  # Convert dict to nested Config object
                v = create_config_dict(v)

            # Sets attributes directly, which is handled under the hood by the __setattr__ function
            self.__setattr__(k, v)

    def __setattr__(self, name: str, value: Any):
        """
        Sets or updates an attribute in the `Config` object.

        If the attribute name starts with an underscore (private attribute), it is set directly in the instance's `__dict__`.
        Otherwise, the attribute is added or updated in the `ConfigAttributes` object. If the value is a dictionary,
        it is converted into a nested `Config` object.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute. If it is a dictionary, it will be converted into a nested `Config` object.
        """

        if name.startswith("_"):
            # Directly set attributes that start with an underscore
            # These are private internal values (like __attributes and __interace)
            self.__dict__[name] = value
        else:
            attributes = self.__dict__["__attributes"]

            # Add or update the existing attribute in ConfigAttributes
            attributes.add_or_update_attribute(name, value)
    
    def __delattr__(self, name: str):
        """
        Deletes an attribute from the `Config` object.
        
        Args:
            name (str): The name of the attribute to delete.
        """
        if name.startswith("_"):
            # For private attributes, delete from __dict__
            del self.__dict__[name]
        else:
            attributes = self.__dict__["__attributes"]
            attributes.remove_attribute(name)

    def __getattr__(self, name):
        """
        Retrieves an attribute from the `Config` object.

        This method is called only if the attribute is not found by the `__getattribute__` method.
        That's an internal Python functionality, not one we've explicitly coded.
        It first checks if the attribute exists in the `ConfigInterface`. If not, it attempts to
        retrieve the attribute based on the current environment. If the attribute is still not found,
        it checks the `ConfigAttributes` object.

        This way, we prioritize the public functions of Config (such as `add_validator`) over attributes.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """

        interface = object.__getattribute__(self, "__interface")

        # First choice is check if this is an interface attribute first, prioritizing public facing functions
        if hasattr(interface, name):
            return getattr(interface, name)

        # Second choice is check if our interface has environment mode enabled which effectively aliases attribute access
        environment = interface.environment

        if environment:
            if name == "environments":
                return getattr(self, name)
            try:
                return getattr(getattr(self, environment), name)
            except AttributeError:
                pass

        # Last choice is directly checking config attributes
        attributes = object.__getattribute__(self, "__attributes")
        
        attr = attributes.get_attribute(name)

        return _chain_return_helper(self, attr)

    def __getattribute__(self, name):
        """
        Retrieves an attribute from the `Config` object, with higher priority in the Python interpreter than `__getattr__`.

        The `__getattribute__` method is a more powerful attribute override and is called for every attribute access.
        It allows for more control over attribute access and is used to implement custom behavior for retrieving attributes.
        This method is necessary because it provides a way to intercept all attribute access attempts, allowing for
        environment-specific lookups and wrapping values in `ValueWrapper`.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """

        if name.startswith("_"):
            # Directly return attributes that start with an underscore
            # These are private attributes used for internal Config functionality
            return object.__getattribute__(self, name)

        interface = object.__getattribute__(self, "__interface")

        if hasattr(interface, name):
            # Defer to getattr function above if it's an interface attribute
            return getattr(interface, name)

        attributes = object.__getattribute__(self, "__attributes")

        # Retrieve the attribute from the ConfigAttributes instance
        attr = attributes.get_attribute(name)

        if isinstance(attr, Config):
            return attr  # Directly return config instance if it's a Config
        else:
            # Otherwise return a ValueWrapped instance of the attribute
            return ValueWrapper.factory(attr)

    def __getitem__(self, key):
        """
        Retrieve an attribute using subscript notation.

        Args:
            key (str): The attribute name to retrieve.

        Returns:
            Any: The value of the attribute.
        """
        return getattr(self, key)

    def __setitem__(self, key, value):
        """
        Set an attribute using subscript notation.

        Args:
            key (str): The attribute name to set.
            value (Any): The value to set the attribute to.
        """
        setattr(self, key, value)

    def __delitem__(self, key):
        """
        Delete an attribute using subscript notation.

        Args:
            key (str): The attribute name to delete.
        """
        attributes = object.__getattribute__(self, "__attributes")
        attributes.remove_attribute(key)

    def __eq__(self, other):
        """
        Compares the `Config` object with another object for equality.

        If the other object is a dictionary, it converts the internal attributes of the `Config` object
        to a dictionary and compares it with the other dictionary. Otherwise, it uses the default
        equality comparison.

        Args:
            other (Any): The object to compare with.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if isinstance(other, dict):
            attributes = object.__getattribute__(self, "__attributes")
            attr = attributes.get_attributes()
            # Convert internal attributes to a dictionary for comparison
            to_dict = {
                k: (
                    v.value
                    if isinstance(v, AbstractConfigItem)
                    else v.to_dict()
                )
                for k, v in attr.items()
            }
            return to_dict == other
        return super().__eq__(other)

    def __str__(self):
        """
        Returns a string representation of the `Config` object.

        This method converts the internal attributes of the `Config` object to a dictionary
        and returns its string representation.

        Returns:
            str: The string representation of the `Config` object.
        """
        get_dict = _get_dict(self)

        str_dict = {}

        for k, v in get_dict.items():
            str_dict[k] = str(v)

        return str(str_dict)
    
    def __iter__(self):
        return iter(_get_dict(self))  # yields keys, like a regular dict

    def __len__(self):
        """
        Returns the number of configuration attributes.
        """
        return len(_get_dict(self))
    
    def __contains__(self, key):
        """
        Checks if the configuration has an attribute.
        """
        return key in _get_dict(self)
