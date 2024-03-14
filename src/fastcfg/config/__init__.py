from abc import ABC


class ConfigMeta():
    pass


class Config():
    def __init__(self, **kwargs):

        self.__meta = ConfigMeta()

        for k, v in kwargs.items():
            setattr(self, k, v)

    def _add_new_attribute(self, name, value):

        if name in self.__dict__:

            if isinstance(self.__dict__[name], Config):

                raise AttributeError(
                    'Cannot override a config object attribute, you must delete it first.')

        super().__setattr__(name, value)

    def __setattr__(self, name, value):
        if name.startswith('__'):
            raise AttributeError(
                'Configs are designed with protected private variables.')
        else:
            self._add_new_attribute(name, value)

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def __str__(self):
        display_dict = {k: v for k,
                        v in self.__dict__.items() if not k.startswith('_')}

        return str(display_dict)
