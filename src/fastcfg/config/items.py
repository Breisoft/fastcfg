from abc import ABC, abstractmethod
from typing import Any

from typing import List

from fastcfg.exceptions import ConfigItemValidationError
from fastcfg.validation import IConfigValidator


class IConfigItem(ABC):

    def __init__(self):
        self._validators: List[IConfigValidator] = []

    @property
    @abstractmethod
    def value(self) -> Any:
        pass

    def add_validator(self, validator: IConfigValidator):
        self._validators.append(validator)

    def validate(self, value: Any):
        for validator in self._validators:
            if not validator.validate(value):
                raise ConfigItemValidationError(validator.error_message())

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

    @property
    def value(self) -> Any:
        self.validate(self._value)
        return self._value


class LiveConfigItem(IConfigItem):

    def __init__(self, state_tracker):

        super().__init__()

        self._state_tracker = state_tracker

    @property
    def value(self) -> Any:
        value = self._state_tracker.get_state()
        self.validate(value)
        return value
