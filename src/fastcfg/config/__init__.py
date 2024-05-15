

from typing import Any

from fastcfg.config.items import IConfigItem, BuiltInConfigItem


class ValueWrapper:
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

    def __init__(self, item):
        self._item = item

    def __getattr__(self, name):
        value = self._item.value
        if isinstance(value, dict):
            if name in value:
                item = value[name]
                if isinstance(item, dict):
                    return Config(**item)
                return item
            else:
                raise AttributeError(
                    f"'{type(value).__name__}' object has no attribute '{name}'")
        try:
            return getattr(value, name)
        except AttributeError:
            return getattr(self._item, name)

    def __getitem__(self, key):
        value = self._item.value[key]

        return value

    def __str__(self):
        return str(self._item.value)

    def __repr__(self):
        return repr(self._item.value)

    def __int__(self):
        return int(self._item.value)

    def __float__(self):
        return float(self._item.value)

    def __bool__(self):
        return bool(self._item.value)

    def __eq__(self, other):
        if isinstance(other, ValueWrapper):
            return self._item.value == other._item.value
        return self._item.value == other

    def __add__(self, other):
        if isinstance(other, ValueWrapper):
            return self._item.value + other._item.value
        return self._item.value + other

    def __radd__(self, other):
        return self.__add__(other)

    @property
    def __class__(self):
        return type(self._item.value)


class ConfigMeta():

    def __init__(self):

        self.__attributes: dict[str, IConfigItem] = {}

    def get_attribute(self, name):

        try:
            return self.__attributes[name]
        except KeyError as exc:
            raise AttributeError(
                f'Attribute `{name}` does not exist.') from exc

    def _convert_value_to_item(self, value: Any) -> IConfigItem:

        if isinstance(value, IConfigItem):
            return value

        elif isinstance(value, Config):
            return value

        elif isinstance(value, (int, float, str, bool, list, dict, tuple, set, object)):
            return BuiltInConfigItem(value)

        else:
            raise ValueError('Invalid data type!')

    def add_new_attribute(self, name, value):

        self.__attributes[name] = self._convert_value_to_item(value)


class Config():
    def __init__(self, **kwargs):
        self.__dict__['__meta'] = ConfigMeta()

        for k, v in kwargs.items():
            # if isinstance(v, dict):
            #    v = Config(**v)

            self.__setattr__(k, v)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            if isinstance(value, dict):
                value = Config(**value)
            meta = self.__dict__['__meta']
            meta.add_new_attribute(name, value)

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        else:
            meta = object.__getattribute__(self, '__meta')

            attr = meta.get_attribute(name)

            if isinstance(attr, Config):
                return attr
            else:
                # Cover IConfigItem in ValueWrapper.
                # See class docstring for explanation as to why.
                return ValueWrapper(meta.get_attribute(name))

    def __str__(self):
        display_dict = {k: v for k,
                        v in self.__meta.__dict__.items() if not k.startswith('_')}

        return str(display_dict)
