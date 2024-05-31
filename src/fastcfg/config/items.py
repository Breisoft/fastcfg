from abc import ABC, abstractmethod
from typing import Any

from fastcfg.exceptions import InvalidOperationError
from fastcfg.validation.validatable import ValidatableMixin

from fastcfg.config.value_wrapper import ValueWrapper

from typing import Dict


class AbstractConfigItem(ValidatableMixin, ABC):
    """
    The `AbstractConfigItem` class serves as an abstract base class for configuration items in the `fastcfg` module.

    Purpose:
        - The primary purpose of the `AbstractConfigItem` class is to define a common interface and shared functionality for all configuration items.
        - It ensures that all configuration items can be validated and have a consistent way of getting and setting their values.
        - This class also provides mechanisms to handle nested dictionary values by wrapping them in `ValueWrapper` instances.
        - By using `AbstractConfigItem` as the base class for configuration attributes, the `Config` class can manage different types of configuration items uniformly.
        - The design choice to use `AbstractConfigItem` allows for flexibility and extensibility, enabling the creation of custom configuration items (e.g., `BuiltInConfigItem`, `LiveConfigItem`) that can have specialized behavior.
        - The `ValueWrapper` class leverages `AbstractConfigItem` to provide seamless interaction with both the underlying value and the configuration item's methods, ensuring that validation and other functionalities are consistently applied.
    Features:
        - **Validation**: Inherits from `ValidatableMixin` to provide validation capabilities.
        - **Abstract Methods**: Defines abstract methods `_get_value` and `_set_value` that must be implemented by subclasses.
        - **Value Handling**: Provides a `value` property to get and set the configuration item's value, with special handling for dictionary values.
        - **Dynamic Attribute Access**: Implements `__getattr__` to suppress type hint errors and handle dynamic attribute access.

    Attributes:
        _wrapped_dict_items (Dict[str, AbstractConfigItem]): A dictionary to store wrapped dictionary items.

    Methods:
        __init__(): Initializes the `AbstractConfigItem` object.
        value: Property to get and set the configuration item's value.
        _get_value(): Abstract method to get the configuration item's value.
        _set_value(new_value): Abstract method to set the configuration item's value.
        __getattr__(name): Dynamically handles attribute access to suppress type hint errors.
    """

    def __init__(self):
        super().__init__()

        self._wrapped_dict_items: Dict[str, AbstractConfigItem] = {}

    @property
    def value(self) -> Any:
        """
        Gets the value of the configuration item.

        This property retrieves the value of the configuration item by calling the `_get_value` method.
        If the value is a dictionary, it wraps the dictionary items in `ValueWrapper` instances to ensure
        consistent interaction with both the underlying value and the configuration item's methods.

        The `value` is implemented as a property instead of a direct attribute to provide controlled access
        and allow for additional processing (such as wrapping dictionary values) when the value is retrieved.

        Returns:
            Any: The value of the configuration item. If the value is a dictionary, the dictionary items are wrapped in `ValueWrapper` instances.
        """

        val = self._get_value()

        return_item = val

        if isinstance(val, dict):
            # Iterate over each key-value pair in the dictionary
            for k, v in val.items():

                # If the key is not already wrapped, wrap it in a ValueWrapper
                if k not in self._wrapped_dict_items:
                    self._wrapped_dict_items[k] = ValueWrapper.factory(
                        BuiltInConfigItem(v))

            # Set the return item to the wrapped dictionary items
            return_item = self._wrapped_dict_items

        return return_item

    @abstractmethod
    def _get_value(self) -> Any:
        """
        Abstract method to get the underlying value of the configuration item.

        This method must be implemented by subclasses to define how the value of the configuration item
        is retrieved. It is called by the `value` property to obtain the current value of the configuration item.

        Returns:
            Any: The current value of the configuration item.
        """

    @value.setter
    def value(self, new_value: Any) -> None:
        self._set_value(new_value)

    def _set_value(self, new_value: Any):
        """
        Sets the value of the configuration item.

        This setter method allows the value of the configuration item to be updated. It calls the `_set_value` method,
        which must be implemented by subclasses to define how the value is set.

        Args:
            new_value (Any): The new value to set for the configuration item.
        """
        raise InvalidOperationError(
            'Can only set value on BuiltInConfigItem')

    def __getattr__(self, name):
        """
        Suppresses type hint errors by dynamically handling attribute access.

        This method is primarily for IDEs and linters to prevent type hint errors
        when accessing attributes that may not be explicitly defined in the class.
        It does not actually provide any meaningful functionality and is essentially
        dead code. If the attribute does not exist, it raises an AttributeError.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            Any: The value of the dynamically accessed attribute, if it existed.

        Raises:
            AttributeError: Always, since the attribute does not actually exist.
        """
        try:
            data = {}
            return data[name]
        except KeyError as exc:
            raise AttributeError(
                f"'ConfigItem' object has no attribute '{name}'") from exc


class BuiltInConfigItem(AbstractConfigItem):
    """
    The `BuiltInConfigItem` class represents a configuration item that holds a built-in data type value.

    Purpose:
        - This concrete class is used to wrap built-in data types (e.g., int, float, str) as configuration items.
        - It provides implementations for the abstract methods `_get_value` and `_set_value` defined in `AbstractConfigItem`.
        - It's used for static data types which don't change unless the attribute itself is directly modified.

    Attributes:
        _value (Any): The underlying value of the configuration item.

    Methods:
        __init__(value: Any): Initializes the `BuiltInConfigItem` with the given value.
        _get_value() -> Any: Retrieves the underlying value of the configuration item.
        _set_value(new_value: Any): Sets the underlying value of the configuration item.
    """

    def __init__(self, value: Any):
        """
        Initializes the `BuiltInConfigItem` with the given value.

        Args:
            value (Any): The initial value of the configuration item.
        """
        super().__init__()
        self._value = value

    def _get_value(self) -> Any:
        """
        Retrieves the underlying value of the configuration item.

        Returns:
            Any: The current value of the configuration item.
        """
        return self._value

    def _set_value(self, new_value: Any):
        """
        Sets the underlying value of the configuration item.

        Args:
            new_value (Any): The new value to set for the configuration item.
        """
        self._value = new_value


class LiveConfigItem(AbstractConfigItem):

    """
    The `LiveConfigItem` class represents a configuration item that is dynamically calculated upon access.

    Purpose:
        - This class is used for configuration items that need to be dynamically validated based on an external state.
        - It provides implementations for the abstract methods `_get_value` and `_set_value` defined in `AbstractConfigItem`.
        - Unlike `BuiltInConfigItem`, it does not allow direct setting of its value.

    Attributes:
        _state_tracker (StateTracker): An external state tracker that provides the current state for the configuration item.

    Methods:
        __init__(state_tracker): Initializes the `LiveConfigItem` with the given state tracker.
        _get_value() -> Any: Retrieves the current state from the state tracker.
        _set_value(new_value: Any): Raises an exception as direct setting of value is not allowed.
        value: Property to get the current state and trigger validation.
    """

    def __init__(self, state_tracker):
        """
            Initializes the `LiveConfigItem` with the given state tracker.

            Args:
                state_tracker (Any): An external state tracker that provides the current state for the configuration item.
            """
        super().__init__()
        self._state_tracker = state_tracker

    @property
    def value(self) -> Any:
        """
        Gets the current state of the configuration item and triggers validation.

        This property retrieves the current state from the state tracker by calling the `_get_value` method.
        It also triggers validation to ensure the state is valid.

        Returns:
            Any: The current state of the configuration item.
        """
        val = super().value

        # Trigger validation
        self.validate()

        return val

    def _get_value(self) -> Any:
        """
        Retrieves the current state from the state tracker.

        This method is called by the `value` property to obtain the current state of the configuration item.

        Returns:
            Any: The current state of the configuration item.
        """

        state = self._state_tracker.get_state()

        return state
