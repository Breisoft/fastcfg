

from typing import Any

from fastcfg.config.items import IConfigItem, BuiltInConfigItem
from fastcfg.exceptions import MissingConfigKeyError


class ValueWrapper:
    def __init__(self, item):
        self._item = item

    def __getattr__(self, name):
        # Delegate attribute access to the underlying value or the item itself
        try:
            return getattr(self._item.value, name)
        except AttributeError:
            return getattr(self._item, name)

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
            self.__setattr__(k, v)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
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
                return ValueWrapper(meta.get_attribute(name))

    def __str__(self):
        display_dict = {k: v for k,
                        v in self.__meta.__dict__.items() if not k.startswith('_')}

        return str(display_dict)
