from typing import TYPE_CHECKING, Any, Union
import operator

from fastcfg.config.utils import create_config_dict

if TYPE_CHECKING:
    from fastcfg.config.items import AbstractConfigItem
else:
    AbstractConfigItem = None


class OperatorsMixin:
    """
    Mixin class that provides operator overloading for ValueWrapper.
    
    This class implements all the magic methods needed to make a wrapped value
    behave like its underlying value in various operations by using Python's
    operator module for proper delegation.
    """
    
    def _unwrap_if_wrapper(self, other):
        """Helper method to unwrap ValueWrapper instances."""
        if isinstance(other, ValueWrapper):
            return other._item.value
        return other
    
    # Comparison operators
    def __lt__(self, other):
        """Less than comparison."""
        return operator.lt(self._item.value, self._unwrap_if_wrapper(other))
    
    def __le__(self, other):
        """Less than or equal comparison."""
        return operator.le(self._item.value, self._unwrap_if_wrapper(other))
    
    def __gt__(self, other):
        """Greater than comparison."""
        return operator.gt(self._item.value, self._unwrap_if_wrapper(other))
    
    def __ge__(self, other):
        """Greater than or equal comparison."""
        return operator.ge(self._item.value, self._unwrap_if_wrapper(other))
    
    def __eq__(self, other):
        """Equal comparison."""
        return operator.eq(self._item.value, self._unwrap_if_wrapper(other))
    
    def __ne__(self, other):
        """Not equal comparison."""
        return operator.ne(self._item.value, self._unwrap_if_wrapper(other))
    
    # Arithmetic operators
    def __add__(self, other):
        """Addition."""
        return operator.add(self._item.value, self._unwrap_if_wrapper(other))
    
    def __radd__(self, other):
        """Reverse addition."""
        return operator.add(self._unwrap_if_wrapper(other), self._item.value)
    
    def __sub__(self, other):
        """Subtraction."""
        return operator.sub(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rsub__(self, other):
        """Reverse subtraction."""
        return operator.sub(self._unwrap_if_wrapper(other), self._item.value)
    
    def __mul__(self, other):
        """Multiplication."""
        return operator.mul(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rmul__(self, other):
        """Reverse multiplication."""
        return operator.mul(self._unwrap_if_wrapper(other), self._item.value)
    
    def __truediv__(self, other):
        """True division."""
        return operator.truediv(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rtruediv__(self, other):
        """Reverse true division."""
        return operator.truediv(self._unwrap_if_wrapper(other), self._item.value)
    
    def __floordiv__(self, other):
        """Floor division."""
        return operator.floordiv(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rfloordiv__(self, other):
        """Reverse floor division."""
        return operator.floordiv(self._unwrap_if_wrapper(other), self._item.value)
    
    def __mod__(self, other):
        """Modulo operation."""
        return operator.mod(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rmod__(self, other):
        """Reverse modulo operation."""
        return operator.mod(self._unwrap_if_wrapper(other), self._item.value)
    
    def __pow__(self, other, modulo=None):
        """Power operation."""
        if modulo is None:
            return operator.pow(self._item.value, self._unwrap_if_wrapper(other))
        return pow(self._item.value, self._unwrap_if_wrapper(other), modulo)
    
    def __rpow__(self, other):
        """Reverse power operation."""
        return operator.pow(self._unwrap_if_wrapper(other), self._item.value)
    
    # Unary operators
    def __neg__(self):
        """Unary negation."""
        return operator.neg(self._item.value)
    
    def __pos__(self):
        """Unary positive."""
        return operator.pos(self._item.value)
    
    def __abs__(self):
        """Absolute value."""
        return operator.abs(self._item.value)
    
    # Bitwise operators
    def __and__(self, other):
        """Bitwise AND."""
        return operator.and_(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rand__(self, other):
        """Reverse bitwise AND."""
        return operator.and_(self._unwrap_if_wrapper(other), self._item.value)
    
    def __or__(self, other):
        """Bitwise OR."""
        return operator.or_(self._item.value, self._unwrap_if_wrapper(other))
    
    def __ror__(self, other):
        """Reverse bitwise OR."""
        return operator.or_(self._unwrap_if_wrapper(other), self._item.value)
    
    def __xor__(self, other):
        """Bitwise XOR."""
        return operator.xor(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rxor__(self, other):
        """Reverse bitwise XOR."""
        return operator.xor(self._unwrap_if_wrapper(other), self._item.value)
    
    def __lshift__(self, other):
        """Left shift."""
        return operator.lshift(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rlshift__(self, other):
        """Reverse left shift."""
        return operator.lshift(self._unwrap_if_wrapper(other), self._item.value)
    
    def __rshift__(self, other):
        """Right shift."""
        return operator.rshift(self._item.value, self._unwrap_if_wrapper(other))
    
    def __rrshift__(self, other):
        """Reverse right shift."""
        return operator.rshift(self._unwrap_if_wrapper(other), self._item.value)
    
    def __invert__(self):
        """Bitwise NOT."""
        return operator.invert(self._item.value)
    
    # Container operations
    def __len__(self):
        """Return length of the underlying value."""
        return len(self._item.value)
    
    def __getitem__(self, key):
        """Get item from the underlying value."""
        return operator.getitem(self._item.value, key)
    
    def __setitem__(self, key, value):
        """Set item in the underlying value."""
        return operator.setitem(self._item.value, key, value)
    
    def __delitem__(self, key):
        """Delete item from the underlying value."""
        return operator.delitem(self._item.value, key)
    
    def __contains__(self, item):
        """Check if item is in the underlying value."""
        return operator.contains(self._item.value, item)
    
    def __iter__(self):
        """Return iterator over the underlying value."""
        return iter(self._item.value)
    
    def __reversed__(self):
        """Return reversed iterator over the underlying value."""
        return reversed(self._item.value)
    
    # String representations
    def __str__(self):
        """Return string representation of the underlying value."""
        return str(self._item.value)
    
    def __repr__(self):
        """Return official string representation of the underlying value."""
        return repr(self._item.value)
    
    def __format__(self, format_spec):
        """Format the underlying value."""
        return format(self._item.value, format_spec)
    
    def __bytes__(self):
        """Return bytes representation of the underlying value."""
        # bytes() constructor behavior depends on the type
        return bytes(self._item.value)
       
    
    # Type conversions
    def __int__(self):
        """Convert to integer."""
        return int(self._item.value)
    
    def __float__(self):
        """Convert to float."""
        return float(self._item.value)
    
    def __complex__(self):
        """Convert to complex number."""
        return complex(self._item.value)
    
    def __bool__(self):
        """Convert to boolean."""
        return bool(self._item.value)
    
    def __index__(self):
        """Convert to integer for use as index."""
        return operator.index(self._item.value)
    
    def __round__(self, ndigits=None):
        """Round the underlying value."""
        if ndigits is None:
            return round(self._item.value)
        return round(self._item.value, ndigits)
    
    def __trunc__(self):
        """Truncate the underlying value."""
        import math
        return math.trunc(self._item.value)
    
    def __floor__(self):
        """Floor of the underlying value."""
        import math
        return math.floor(self._item.value)
    
    def __ceil__(self):
        """Ceiling of the underlying value."""
        import math
        return math.ceil(self._item.value)
    
    # Hash support
    def __hash__(self):
        """Return hash of the underlying value."""
        return hash(self._item.value)


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
        if hasattr(self._item, name) and not name.startswith('_'):
            attr = getattr(self._item, name)
            return attr

        # For dictionaries that are Config objects, we need special handling
        if hasattr(value, '__class__') and value.__class__.__name__ == 'ConfigInterface':
            # Try to get from the Config object's attributes first
            try:
                return getattr(value, name)
            except AttributeError:
                # If not found, try as a key
                if name in value:
                    return value[name]
                raise

        if isinstance(value, dict):
            if name in value:
                item = value[name]
                if isinstance(item, dict):
                    return create_config_dict(item)
                return item
            else:
                # Try to get dict methods
                if hasattr(dict, name):
                    return getattr(value, name)
                raise AttributeError(
                    f"'{type(value).__name__}' object has no attribute '{name}'"
                )
        
        # For all other types, try to get the attribute from the value
        return getattr(value, name)

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

