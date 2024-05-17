

from typing import Any

from fastcfg.config.items import IConfigItem, BuiltInConfigItem

from fastcfg.config.utils import create_config_dict

from fastcfg.config.value_wrapper import ValueWrapper

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

        elif isinstance(value, BUILT_IN_TYPES):
            return BuiltInConfigItem(value)

        else:
            raise ValueError('Invalid data type!')

    def add_new_attribute(self, name, value):

        self.__attributes[name] = self._convert_value_to_item(value)


class Config():
    def __init__(self, **kwargs):
        self.__dict__['__meta'] = ConfigMeta()
        self.__dict__['_current_env'] = None

        for k, v in kwargs.items():
            if isinstance(v, dict):
                v = create_config_dict(v)

            self.__setattr__(k, v)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            if isinstance(value, dict):
                value = create_config_dict(value)
            meta = self.__dict__['__meta']
            meta.add_new_attribute(name, value)

    def add_validator(self, validator):
        # NOTE do we need to remove this or do something here?
        pass

    def set_environment(self, env):
        self._current_env = env

    def __getattr__(self, name):
        if self._current_env:
            try:
                return getattr(self._current_env, name)
            except AttributeError:
                pass
        meta = self.__dict__['__meta']
        return meta.get_attribute(name)

    def __getattribute__(self, name):

        if name.startswith('_') or name in {'add_validator', 'validate', 'set_environment'}:
            return object.__getattribute__(self, name)
        else:
            meta = object.__getattribute__(self, '__meta')

            attr = meta.get_attribute(name)

            if isinstance(attr, Config):
                return attr
            else:
                # Cover IConfigItem in ValueWrapper.
                # See class docstring for explanation as to why.
                return ValueWrapper.factory(meta.get_attribute(name))

    def __eq__(self, other):
        if isinstance(other, dict):
            meta = self.__getattribute__('__meta')
            attributes = meta.__getattribute__('_ConfigMeta__attributes')
            to_dict = {k: v.value if isinstance(
                v, IConfigItem) else v.to_dict() for k, v in attributes.items()}
            return to_dict == other
        return super().__eq__(other)

    def __str__(self):
        display_dict = {k: v for k,
                        v in self.__dict__['__meta'].__dict__.items() if not k.startswith('_')}

        return str(display_dict)
