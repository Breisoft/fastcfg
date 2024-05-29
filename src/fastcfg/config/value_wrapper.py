from fastcfg.config.utils import create_config_dict


class ValueWrapper():
    """
    A wrapper class that allows treating an instance of IConfigItem as equivalent to its underlying value.
    This class delegates attribute access to the underlying value or the item itself, enabling seamless
    interaction with both the value and the IConfigItem's methods.

    This is useful for scenarios where you want to work directly with the value of a configuration item
    while still being able to access and utilize the methods of the IConfigItem, such as add_validator.

    Example:
        config = Config()
        config.my_number = 42 # Automatically wraps built-in types with a BuiltInConfigItem

        # Accessing the value directly
        print(config.my_number)  # Output: 42

        print(config.my_number + config.my_number) # Output 84

        # Using IConfigItem methods
        config.my_number.add_validator(RangeValidator(1, 50))
    """

    @staticmethod
    def factory(obj):

        return ValueWrapper(obj)

    @staticmethod
    def unwrap(value):
        if isinstance(value, ValueWrapper):
            return ValueWrapper.unwrap(value._item.value)
        elif isinstance(value, dict):
            return {k: ValueWrapper.unwrap(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [ValueWrapper.unwrap(v) for v in value]
        return value

    def __init__(self, item):
        """
        Initialize the ValueWrapper with an IConfigItem instance.

        Args:
            item (IConfigItem): The configuration item to wrap.
        """
        self._item = item

    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying value or the IConfigItem instance.

        This method first tries to access the attribute from the underlying value. If the value is a dictionary,
        it attempts to retrieve the item from the dictionary. If the item is also a dictionary, it converts it to a Config instance.
        If the attribute is not found in the dictionary, it raises an AttributeError.

        If the value is not a dictionary, it tries to get the attribute from the value directly. If that fails,
        it falls back to getting the attribute from the IConfigItem instance.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist in the value or the IConfigItem instance.
        """
        value = self._item.value

        # Check if the attribute is a public method of IConfigItem)
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
                    f"'{type(value).__name__}' object has no attribute '{name}'")
        try:
            return getattr(value, name)
        except AttributeError:
            return getattr(self._item, name)

    def __getitem__(self, key):
        """
        Allow dictionary-like access to the underlying value.

        Args:
            key (Any): The key to access in the underlying value.

        Returns:
            Any: The value associated with the key.
        """
        value = self._item.value[key]
        return value

    def __str__(self):
        """
        Return the string representation of the underlying value.

        Returns:
            str: The string representation of the value.
        """
        return str(self._item.value)

    def __repr__(self):
        """
        Return the official string representation of the underlying value.

        Returns:
            str: The official string representation of the value.
        """
        return repr(self._item.value)

    def __int__(self):
        """
        Convert the underlying value to an integer.

        Returns:
            int: The integer representation of the value.
        """
        return int(self._item.value)

    def __float__(self):
        """
        Convert the underlying value to a float.

        Returns:
            float: The float representation of the value.
        """
        return float(self._item.value)

    def __bool__(self):
        """
        Convert the underlying value to a boolean.

        Returns:
            bool: The boolean representation of the value.
        """
        return bool(self._item.value)

    def __eq__(self, other):
        """
        Compare the underlying value with another value.

        Args:
            other (Any): The value to compare with.

        Returns:
            bool: True if the values are equal, False otherwise.
        """
        if isinstance(other, ValueWrapper):
            return self._item.value == other._item.value
        return self._item.value == other

    def __add__(self, other):
        """
        Add the underlying value to another value.

        Args:
            other (Any): The value to add.

        Returns:
            Any: The result of the addition.
        """
        if isinstance(other, ValueWrapper):
            return self._item.value + other._item.value
        return self._item.value + other

    def __radd__(self, other):
        """
        Add the underlying value to another value (reversed operands).

        Args:
            other (Any): The value to add.

        Returns:
            Any: The result of the addition.
        """
        return self.__add__(other)

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
