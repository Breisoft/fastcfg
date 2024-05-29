from fastcfg.exceptions import ConfigItemValidationError
from fastcfg.validation import IConfigValidator
from abc import ABC, abstractmethod
from typing import Any

from typing import List


from fastcfg.config.items import IConfigItem, BuiltInConfigItem

BUILT_IN_TYPES = (
    int,
    float,
    str,
    bool,
    list,
    dict,
    tuple,
    set,
    object
)


class ConfigAttributes():
    """
    Manages the actual configuration values, ensuring they are stored and retrieved correctly.
    This class acts as a proxy for the Config class, allowing it to handle unique attribute management efficiently.
    By separating attribute storage and retrieval into its own class, the Config class remains clean and focused on its primary responsibilities.
    """

    def __init__(self):

        self.__attributes: dict[str, IConfigItem] = {}

    def get_attribute(self, name):

        try:
            return self.__attributes[name]
        except KeyError as exc:
            raise AttributeError(
                f'Attribute `{name}` does not exist.') from exc

    def get_attributes(self):
        return self.__attributes

    def _convert_value_to_item(self, value: Any) -> IConfigItem:

        from fastcfg.config import Config

        if isinstance(value, IConfigItem):
            return value

        elif isinstance(value, Config):
            return value

        elif isinstance(value, BUILT_IN_TYPES):
            return BuiltInConfigItem(value)

        else:
            raise ValueError('Invalid data type!')

    def _add_attribute(self, name: str, value: Any) -> IConfigItem:
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

    def add_or_update_attribute(self, name: str, value: Any):
        """
        Adds a new attribute or updates an existing attribute in the configuration.

        If the attribute already exists and is a BuiltInConfigItem, its value is updated.
        If the attribute is a LiveConfigItem, it is replaced with a new value.
        If the attribute does not exist, it is added as a new attribute.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute, which will be converted to an IConfigItem.
        """

        if name in self.__attributes:  # Existing attribute that we're overriding
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
