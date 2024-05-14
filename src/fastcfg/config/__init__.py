

from typing import Any

from fastcfg.config.items import IConfigItem, BuiltInConfigItem
from fastcfg.exceptions import MissingConfigKeyError


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
        """
        if name in self.__attributes:

            if isinstance(self.__attributes[name], Config):

                raise AttributeError(
                    'Cannot override a config object attribute, you must delete it first.')
        """

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
                return meta.get_attribute(name).value

    def __str__(self):
        display_dict = {k: v for k,
                        v in self.__meta.__dict__.items() if not k.startswith('_')}

        return str(display_dict)
