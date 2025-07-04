"""
This module defines the configuration item classes for the `fastcfg` module. 
These are used as interfaces to interact with when accessing configuration attributes.

Classes:
    AbstractConfigItem: An abstract base class for configuration items, providing a common interface and shared functionality.
    BuiltInConfigItem: A concrete class representing configuration items that hold built-in data type values.
    LiveConfigItem: A concrete class representing configuration items that are dynamically calculated upon access.

Usage Examples:

    ```python
    # Creating a BuiltInConfigItem
    config.item = 42 # Automatically wraps the value in a BuiltInConfigItem
    print(config.item.value)  # Output: 42
    config.item.value = 100
    print(config.item.value)  # Output: 100

    # Creating a LiveConfigItem with a state tracker
    class StateTracker:
        def get_state(self):
            return "dynamic_value"

    state_tracker = StateTracker()
    live_item = LiveConfigItem(state_tracker)
    print(live_item.value)  # Output: "dynamic_value"
    ```
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from fastcfg.config.value_wrapper import ValueWrapper
from fastcfg.exceptions import InvalidOperationError
from fastcfg.validation.validatable import ValidatableMixin
from fastcfg.config.events import EventListenerMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastcfg.config.interface import Config
else:
    Config = None

def _notify_if_changed(config_item, old_value, new_value):
    """
    Helper function to notify listeners if a configuration value has changed.
    
    This function encapsulates the change detection and notification logic
    to avoid code duplication between different change scenarios.
    
    Args:
        config_item: The configuration item that potentially changed
        old_value: The previous value
        new_value: The current value
    """
    if old_value != new_value:
        config_item.notify_change(config_item, old_value, new_value)


class AbstractConfigItem(ValidatableMixin, EventListenerMixin, ABC):
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

        self._parent: 'Config' = None

    def set_parent(self, parent: 'Config'):
        self._parent = parent

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
                        BuiltInConfigItem(v)
                    )

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

    def as_callable(self):
        """
        Raises:
            TypeError: If the configuration item is not a LiveConfigItem.
        """
        raise TypeError("Can only call as_callable on LiveConfigItem")

    def _set_value(self, new_value: Any):
        """
        Sets the value of the configuration item.

        This setter method allows the value of the configuration item to be updated. It calls the `_set_value` method,
        which must be implemented by subclasses to define how the value is set.

        Args:
            new_value (Any): The new value to set for the configuration item.
        """
        raise InvalidOperationError("Can only set value on BuiltInConfigItem")

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
                f"'ConfigItem' object has no attribute '{name}'"
            ) from exc

    def __str__(self) -> str:
        return str(self.value)


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

        old_value = self._value
        self._value = new_value

        # This is done separately for BuiltInConfigItems
        # and LiveConfigItems. LCIs don't support direct setting of value.
        _notify_if_changed(self, old_value, new_value)


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

        # Track the previous value to avoid unnecessary event notifications
        self._previous_value = None

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

        # Check for changes from external sources and notify if changed
        _notify_if_changed(self, self._previous_value, val)
        
        # Always update previous value after potential notification
        self._previous_value = val

        # Return the value
        return val
    
    def as_callable(self):
        """
        Returns a callable that always returns the current state of the configuration item.

        Returns:
            Callable: A callable that always returns the current state of the configuration item.
        """
        return lambda: self.value

    def _get_value(self) -> Any:
        """
        Retrieves the current state from the state tracker.

        This method is called by the `value` property to obtain the current state of the configuration item.

        Returns:
            Any: The current state of the configuration item.
        """

        state = self._state_tracker.get_state()

        return state
