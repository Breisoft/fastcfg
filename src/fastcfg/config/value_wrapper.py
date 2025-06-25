from typing import TYPE_CHECKING, Any, Union

from fastcfg.config.utils import create_config_dict

if TYPE_CHECKING:
    from fastcfg.config.items import AbstractConfigItem
else:
    AbstractConfigItem = None


class OperatorsMixin:
    """
    Mixin class that provides operator overloading for ValueWrapper.
    
    This class implements all the magic methods needed to make a wrapped value
    behave like its underlying value in various operations by delegating
    directly to the underlying value's methods.
    """
    
    def _unwrap_if_wrapper(self, other):
        """Helper method to unwrap ValueWrapper instances."""
        if isinstance(other, ValueWrapper):
            return other._item.value
        return other
    
    # Comparison operators
    def __lt__(self, other):
        """Less than comparison."""
        return self._item.value.__lt__(self._unwrap_if_wrapper(other))
    
    def __le__(self, other):
        """Less than or equal comparison."""
        return self._item.value.__le__(self._unwrap_if_wrapper(other))
    
    def __gt__(self, other):
        """Greater than comparison."""
        return self._item.value.__gt__(self._unwrap_if_wrapper(other))
    
    def __ge__(self, other):
        """Greater than or equal comparison."""
        return self._item.value.__ge__(self._unwrap_if_wrapper(other))
    
    def __eq__(self, other):
        """Equal comparison."""
        return self._item.value.__eq__(self._unwrap_if_wrapper(other))
    
    def __ne__(self, other):
        """Not equal comparison."""
        return self._item.value.__ne__(self._unwrap_if_wrapper(other))
    
    # Arithmetic operators
    def __add__(self, other):
        """Addition."""
        return self._item.value.__add__(self._unwrap_if_wrapper(other))
    
    def __radd__(self, other):
        """Reverse addition."""
        return self._item.value.__radd__(other)
    
    def __sub__(self, other):
        """Subtraction."""
        return self._item.value.__sub__(self._unwrap_if_wrapper(other))
    
    def __rsub__(self, other):
        """Reverse subtraction."""
        return self._item.value.__rsub__(other)
    
    def __mul__(self, other):
        """Multiplication."""
        return self._item.value.__mul__(self._unwrap_if_wrapper(other))
    
    def __rmul__(self, other):
        """Reverse multiplication."""
        return self._item.value.__rmul__(other)
    
    def __truediv__(self, other):
        """True division."""
        return self._item.value.__truediv__(self._unwrap_if_wrapper(other))
    
    def __rtruediv__(self, other):
        """Reverse true division."""
        return self._item.value.__rtruediv__(other)
    
    def __floordiv__(self, other):
        """Floor division."""
        return self._item.value.__floordiv__(self._unwrap_if_wrapper(other))
    
    def __rfloordiv__(self, other):
        """Reverse floor division."""
        return self._item.value.__rfloordiv__(other)
    
    def __mod__(self, other):
        """Modulo operation."""
        return self._item.value.__mod__(self._unwrap_if_wrapper(other))
    
    def __rmod__(self, other):
        """Reverse modulo operation."""
        return self._item.value.__rmod__(other)
    
    def __pow__(self, other, modulo=None):
        """Power operation."""
        if modulo is None:
            return self._item.value.__pow__(self._unwrap_if_wrapper(other))
        return self._item.value.__pow__(self._unwrap_if_wrapper(other), modulo)
    
    def __rpow__(self, other):
        """Reverse power operation."""
        return self._item.value.__rpow__(other)
    
    # Unary operators
    def __neg__(self):
        """Unary negation."""
        return self._item.value.__neg__()
    
    def __pos__(self):
        """Unary positive."""
        return self._item.value.__pos__()
    
    def __abs__(self):
        """Absolute value."""
        return self._item.value.__abs__()
    
    # Bitwise operators
    def __and__(self, other):
        """Bitwise AND."""
        return self._item.value.__and__(self._unwrap_if_wrapper(other))
    
    def __rand__(self, other):
        """Reverse bitwise AND."""
        return self._item.value.__rand__(other)
    
    def __or__(self, other):
        """Bitwise OR."""
        return self._item.value.__or__(self._unwrap_if_wrapper(other))
    
    def __ror__(self, other):
        """Reverse bitwise OR."""
        return self._item.value.__ror__(other)
    
    def __xor__(self, other):
        """Bitwise XOR."""
        return self._item.value.__xor__(self._unwrap_if_wrapper(other))
    
    def __rxor__(self, other):
        """Reverse bitwise XOR."""
        return self._item.value.__rxor__(other)
    
    def __lshift__(self, other):
        """Left shift."""
        return self._item.value.__lshift__(self._unwrap_if_wrapper(other))
    
    def __rlshift__(self, other):
        """Reverse left shift."""
        return self._item.value.__rlshift__(other)
    
    def __rshift__(self, other):
        """Right shift."""
        return self._item.value.__rshift__(self._unwrap_if_wrapper(other))
    
    def __rrshift__(self, other):
        """Reverse right shift."""
        return self._item.value.__rrshift__(other)
    
    def __invert__(self):
        """Bitwise NOT."""
        return self._item.value.__invert__()
    
    # Container operations
    def __len__(self):
        """Return length of the underlying value."""
        return self._item.value.__len__()
    
    def __getitem__(self, key):
        """Get item from the underlying value."""
        return self._item.value.__getitem__(key)
    
    def __setitem__(self, key, value):
        """Set item in the underlying value."""
        return self._item.value.__setitem__(key, value)
    
    def __delitem__(self, key):
        """Delete item from the underlying value."""
        return self._item.value.__delitem__(key)
    
    def __contains__(self, item):
        """Check if item is in the underlying value."""
        return self._item.value.__contains__(item)
    
    def __iter__(self):
        """Return iterator over the underlying value."""
        return self._item.value.__iter__()
    
    def __reversed__(self):
        """Return reversed iterator over the underlying value."""
        return self._item.value.__reversed__()
    
    # String representations
    def __str__(self):
        """Return string representation of the underlying value."""
        return self._item.value.__str__()
    
    def __repr__(self):
        """Return official string representation of the underlying value."""
        return self._item.value.__repr__()
    
    def __format__(self, format_spec):
        """Format the underlying value."""
        return self._item.value.__format__(format_spec)
    
    def __bytes__(self):
        """Return bytes representation of the underlying value."""
        return self._item.value.__bytes__()
    
    # Type conversions
    def __int__(self):
        """Convert to integer."""
        return self._item.value.__int__()
    
    def __float__(self):
        """Convert to float."""
        return self._item.value.__float__()
    
    def __complex__(self):
        """Convert to complex number."""
        return self._item.value.__complex__()
    
    def __bool__(self):
        """Convert to boolean."""
        return self._item.value.__bool__()
    
    def __index__(self):
        """Convert to integer for use as index."""
        return self._item.value.__index__()
    
    def __round__(self, ndigits=None):
        """Round the underlying value."""
        return self._item.value.__round__(ndigits)
    
    def __trunc__(self):
        """Truncate the underlying value."""
        return self._item.value.__trunc__()
    
    def __floor__(self):
        """Floor of the underlying value."""
        return self._item.value.__floor__()
    
    def __ceil__(self):
        """Ceiling of the underlying value."""
        return self._item.value.__ceil__()
    
    # Hash support
    def __hash__(self):
        """Return hash of the underlying value."""
        return self._item.value.__hash__()


class ValueWrapper(OperatorsMixin):
    """
    A wrapper class that allows treating an instance of AbstractConfigItem as equivalent to its underlying value.
    This class delegates attribute access to the underlying value or the item itself, enabling seamless
    interaction with both the value and the AbstractConfigItem's methods.

    This is useful for scenarios where you want to work directly with the value of a configuration item
    while still being able to access and utilize the methods of the AbstractConfigItem, such as add_validator.

    Example:
        config = Config()
        config.my_number = 42 # Automatically wraps built-in types with a BuiltInConfigItem

        # Accessing the value directly
        print(config.my_number)  # Output: 42

        print(config.my_number + config.my_number) # Output 84

        # Using AbstractConfigItem methods
        config.my_number.add_validator(RangeValidator(1, 50))
    """

    @staticmethod
    def factory(obj) -> "ValueWrapper":

        return ValueWrapper(obj)

    @staticmethod
    def unwrap(
        value: Union[dict, AbstractConfigItem, list, int, float, str, bool]
    ) -> Any:
        if isinstance(value, ValueWrapper):
            return ValueWrapper.unwrap(value._item.value)
        elif isinstance(value, dict):
            return {k: ValueWrapper.unwrap(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [ValueWrapper.unwrap(v) for v in value]
        return value

    def __init__(self, item: AbstractConfigItem):
        """
        Initialize the ValueWrapper with an AbstractConfigItem instance.

        Args:
            item (AbstractConfigItem): The configuration item to wrap.
        """
        self._item = item

    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying value or the AbstractConfigItem instance.

        This method first tries to access the attribute from the underlying value. If the value is a dictionary,
        it attempts to retrieve the item from the dictionary. If the item is also a dictionary, it converts it to a Config instance.
        If the attribute is not found in the dictionary, it raises an AttributeError.

        If the value is not a dictionary, it tries to get the attribute from the value directly. If that fails,
        it falls back to getting the attribute from the AbstractConfigItem instance.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist in the value or the AbstractConfigItem instance.
        """
        value = self._item.value

        # Check if the attribute is a public method of AbstractConfigItem
        if hasattr(self._item, name) and callable(getattr(self._item, name)):
            attr = getattr(self._item, name)
            return attr

        if isinstance(value, dict):
            if name in value:
                item = value[name]
                if isinstance(item, dict):
                    return create_config_dict(item)
                return item
            else:
                raise AttributeError(
                    f"'{type(value).__name__}' object has no attribute '{name}'"
                )
        try:
            return getattr(value, name)
        except AttributeError:
            return getattr(self._item, name)

    @property
    def __class__(self):
        """
        Return the class of the underlying value.

        This property allows the ValueWrapper to mimic the class of the underlying value,
        making it more transparent in type checks and introspection.

        Returns:
                type: The class of the underlying value.
        """
        return type(self._item.value)

