"""
This module provides the `ConfigAttributes` class, which manages configuration attributes and their associated values.

The `ConfigAttributes` class acts as a proxy for the `Config` class, allowing it to handle unique attribute management efficiently. By separating attribute storage and retrieval into its own class, the `Config` class remains clean and focused on its primary responsibilities.
"""

from typing import Any

from fastcfg.config.base import AbstractConfigUnit
from fastcfg.config.items import AbstractConfigItem, BuiltInConfigItem

# Types that are classified as built-in rather than custom objects
BUILT_IN_TYPES = (int, float, str, bool, list, dict, tuple, set, object)


class ConfigAttributes(AbstractConfigUnit):
    """
    Manages the actual configuration attributes and their associated values, ensuring they are stored and retrieved correctly.

    This class acts as a proxy for the `Config` class, allowing it to handle unique attribute management efficiently.
    By separating attribute storage and retrieval into its own class, the `Config` class remains clean and focused on its primary responsibilities.

    Attributes:
        __attributes (dict[str, IConfigItem]): A dictionary to store configuration attributes.

    Methods:
        __init__(): Initializes the `ConfigAttributes` object.
        get_attribute(name): Retrieves an attribute by name.
        get_attributes(): Returns all attributes.
        _convert_value_to_item(value): Converts a value to an `IConfigItem`.
        _add_attribute(name, value): Adds a new attribute to the configuration.
        add_or_update_attribute(name, value): Adds or updates an attribute in the configuration.
    """

    def __init__(self):

        self.__attributes: dict[str, AbstractConfigItem] = {}

    def get_attribute(self, name) -> AbstractConfigItem:
        """
        Retrieves an attribute by name.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            IConfigItem: The configuration item associated with the given name.

        Raises:
            AttributeError: If the attribute does not exist.
        """

        try:
            return self.__attributes[name]
        except KeyError as exc:
            raise AttributeError(
                f"Attribute `{name}` does not exist."
            ) from exc

    def has_attribute(self, name: str) -> bool:
        """
        Returns whether an attribute exists.
        """
        return name in self.__attributes

    def get_attributes(self) -> dict[str, AbstractConfigItem]:
        """
        Returns all attributes.

        Returns:
            dict[str, IConfigItem]: A dictionary of all configuration attributes.
        """
        return self.__attributes

    def _convert_value_to_item(self, value: Any) -> AbstractConfigItem:
        """
        Converts a raw value to an `IConfigItem`.

        Args:
            value (Any): The value to convert.

        Returns:
            IConfigItem: The converted configuration item.

        Raises:
            ValueError: If the value is of an invalid data type.
        """

        from fastcfg.config import Config

        if isinstance(value, AbstractConfigItem):
            return value

        elif isinstance(value, Config):
            return value

        elif isinstance(value, BUILT_IN_TYPES):
            return BuiltInConfigItem(value)

        else:
            raise ValueError("Invalid data type!")

    def _add_attribute(self, name: str, value: Any) -> AbstractConfigItem:
        """
        Adds a new attribute to the configuration.
        Overrides existing IConfigItem if it already exists.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute, which will be converted to an IConfigItem.

        Returns:
            IConfigItem: The newly added configuration item.
        """
        config_item = self._convert_value_to_item(value)

        self.__attributes[name] = config_item

        return config_item

    def add_or_update_attribute(self, name: str, value: Any) -> None:
        """
        Adds a new attribute or updates an existing attribute in the configuration.

        If the attribute already exists and is a BuiltInConfigItem, its value is updated.
        If the attribute is a LiveConfigItem, it is replaced with a new value.
        If the attribute does not exist, it is added as a new attribute.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute, which will be converted to an IConfigItem.
        """

        if (
            name in self.__attributes
        ):  # Existing attribute that we're overriding
            config_item = self.__attributes[name]

            # Only support value overriding for BuiltInConfigItems
            # For LiveConfigItems, we just want to replace it with the new value
            if isinstance(config_item, BuiltInConfigItem):
                config_item.value = value
            else:
                config_item = self._add_attribute(name, value)
        else:  # New attribute entirely
            config_item = self._add_attribute(name, value)

        # Trigger validation at the end
        config_item.validate()

    def remove_attribute(self, name: str) -> None:
        """
        Removes an attribute from the configuration.

        Args:
            name (str): The name of the attribute to remove.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        if name not in self.__attributes:
            raise AttributeError(f"Attribute `{name}` does not exist.")
        del self.__attributes[name]
