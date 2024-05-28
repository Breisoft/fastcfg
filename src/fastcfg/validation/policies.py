import re
from typing import Any
from fastcfg.validation import IConfigValidator
from fastcfg.exceptions import MissingDependencyError, ConfigItemValidationError
from fastcfg.config.value_wrapper import ValueWrapper

try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    BaseModel, ValidationError = None, None


class RangeValidator(IConfigValidator):
    def __init__(self, min_value: int, max_value: int):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> bool:
        return self.min_value <= value <= self.max_value

    def error_message(self) -> str:
        return f"Value must be between {self.min_value} and {self.max_value}."


class TypeValidator(IConfigValidator):
    def __init__(self, expected_type: type):
        self.expected_type = expected_type

    def validate(self, value: Any) -> bool:
        return isinstance(value, self.expected_type)

    def error_message(self) -> str:
        return f"Value must be of type {self.expected_type.__name__}."


class RegexValidator(IConfigValidator):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def validate(self, value: Any) -> bool:
        return bool(re.match(self.pattern, value))

    def error_message(self) -> str:
        return f"Value must match the pattern {self.pattern}."


class PydanticValidator(IConfigValidator):
    def __init__(self, model: BaseModel):
        self.model = model

        self._latest_error = None

    def validate(self, value: Any) -> bool:

        if BaseModel is None:
            raise MissingDependencyError("Pydantic")
        try:
            unwrapped_value = ValueWrapper.unwrap(value)
            self.model.model_validate(unwrapped_value)
            return True
        except ValidationError as exc:
            self._latest_error = exc
            return False

    def error_message(self) -> str:
        msg = f"Value does not conform to the Pydantic model {self.model.__name__}."

        if self._latest_error:
            msg += f' Latest Exception: {self._latest_error}'
