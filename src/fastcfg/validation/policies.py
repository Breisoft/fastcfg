import re
from typing import Any

from fastcfg.config.value_wrapper import ValueWrapper
from fastcfg.exceptions import MissingDependencyError
from fastcfg.validation import IConfigValidator

try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    BaseModel, ValidationError = None, None


class RangeValidator(IConfigValidator):
    def __init__(
        self, min_value: int, max_value: int, validate_immediately: bool = True
    ):

        super().__init__(validate_immediately=validate_immediately)

        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> bool:
        try:
            return self.min_value <= value <= self.max_value
        except TypeError:
            return False

    def error_message(self) -> str:
        return f"Value must support <= operator and be between {self.min_value} and {self.max_value}."


class TypeValidator(IConfigValidator):
    def __init__(self, expected_type: type, validate_immediately: bool = True):
        super().__init__(validate_immediately=validate_immediately)
        self.expected_type = expected_type

    def validate(self, value: Any) -> bool:
        return isinstance(value, self.expected_type)

    def error_message(self) -> str:
        return f"Value must be of type {self.expected_type.__name__}."
    

class LengthValidator(IConfigValidator):
    def __init__(self, length: int, validate_immediately: bool = True):
        super().__init__(validate_immediately=validate_immediately)
        self.length = length

    def validate(self, value: Any) -> bool:
        return len(value) == self.length

    def error_message(self) -> str:
        return f"Value must be of length {self.length}."
    

class RegexValidator(IConfigValidator):
    def __init__(self, pattern: str, validate_immediately: bool = True):
        super().__init__(validate_immediately=validate_immediately)

        self.pattern = pattern

    def validate(self, value: Any) -> bool:
        return bool(re.match(self.pattern, value))

    def error_message(self) -> str:
        return f"Value must match the pattern {self.pattern}."


class URLValidator(RegexValidator):
    def __init__(self, validate_immediately: bool = True):
        # Regular expression pattern to validate URLs
        pattern = r"^https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$"
        super().__init__(pattern, validate_immediately=validate_immediately)

    def error_message(self) -> str:
        return "Value must be a valid URL."


class PydanticValidator(IConfigValidator):
    def __init__(self, model: BaseModel, validate_immediately: bool = True, transform: bool = False):
        super().__init__(validate_immediately=validate_immediately)
        self.model = model

        self._latest_error = None

    def validate(self, value: Any) -> bool:

        if BaseModel is None:
            raise MissingDependencyError("Pydantic")
        try:
            unwrapped_value = ValueWrapper.unwrap(value)
            self.model.model_validate(unwrapped_value)

            # TODO: Transform the value if transform is True
            # This will involve mapping the end result of the model 
            # to the Config object

            return True
        except ValidationError as exc:
            self._latest_error = exc
            return False

    def error_message(self) -> str:
        msg = f"Value does not conform to the Pydantic model {self.model.__name__}."

        if self._latest_error:
            msg += f" Latest Exception: {self._latest_error}"
