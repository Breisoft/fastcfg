from abc import ABC, abstractmethod
from typing import Any

from typing import List

from fastcfg.exceptions import ConfigItemValidationError
from fastcfg.validation import IConfigValidator

from fastcfg.config.value_wrapper import ValueWrapper

from typing import Dict


class IConfigItem(ABC):

    def __init__(self):
        self._validators: List[IConfigValidator] = []

        self._wrapped_dict_items: Dict[str, IConfigItem] = {}

    @property
    def value(self) -> Any:
        val = self._get_value()

        return_item = val

        if isinstance(val, dict):
            for k, v in val.items():

                if k not in self._wrapped_dict_items:
                    self._wrapped_dict_items[k] = ValueWrapper.factory(
                        BuiltInConfigItem(v))

            return_item = self._wrapped_dict_items

        self.validate(return_item)

        return return_item

    @abstractmethod
    def _get_value(self) -> Any:
        pass

    def add_validator(self, validator: IConfigValidator):
        self._validators.append(validator)

    def get_validators(self):
        return self._validators

    def validate(self, value: Any):
        for validator in self._validators:
            if not validator.validate(value):
                raise ConfigItemValidationError(validator.error_message())

        # Recursively validate nested dictionaries
        if isinstance(value, dict):
            for k, v in self._wrapped_dict_items.items():
                v.validate(v.value)

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


class BuiltInConfigItem(IConfigItem):

    def __init__(self, value: Any):
        super().__init__()

        self._value = value

    def _get_value(self) -> Any:
        return self._value


class LiveConfigItem(IConfigItem):

    def __init__(self, state_tracker):

        super().__init__()

        self._state_tracker = state_tracker

    def _get_value(self) -> Any:
        return self._state_tracker.get_state()
