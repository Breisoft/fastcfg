from abc import ABC, abstractmethod
from typing import Any


class IConfigValidator(ABC):

    def __init__(self, validate_immediately: bool = True):
        self.validate_immediately = validate_immediately

    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate the given value."""
        pass

    @abstractmethod
    def error_message(self) -> str:
        """Return the error message if validation fails."""
        pass
