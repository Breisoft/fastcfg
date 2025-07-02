import hashlib
from abc import ABC, abstractmethod
from typing import Any, List

from fastcfg.config import items
from fastcfg.config.utils import potentially_has_children, resolve_all_values
from fastcfg.exceptions import ConfigItemValidationError
from fastcfg.validation import IConfigValidator


def md5_hash_state(input_obj: Any) -> str:
    """Hash LiveConfig object's state"""

    # Convert obj to str
    input_str = str(input_obj)

    # Create an MD5 hash object
    md5_hash = hashlib.md5()

    # Update the hash object with the bytes of the input string
    md5_hash.update(input_str.encode("utf-8"))

    # Get the hexadecimal representation of the hash
    return md5_hash.hexdigest()


class ValidatableMixin(ABC):

    def __init__(self):

        # Ensure any other mixins are also initialized
        super().__init__()

        self._last_state_hash = None  # Used for LiveConfigItem state tracking
        self._validators: List[IConfigValidator] = []

    def add_validator(self, validator: IConfigValidator) -> "ValidatableMixin":
        self._validators.append(validator)

        if validator.validate_immediately:
            # Validate immediately when a new validator is added
            self.validate(force_live=True)

        # Allows for method chaining
        return self

    def get_validators(self):
        """Get the validators for the current validatable item."""
        return self._validators

    def validate(self, force_live: bool = False):
        """
        Validate the current configuration item and its children.

        This method performs validation on the current configuration item and its
        children. If the item is an instance of LiveConfigItem, it uses an MD5 hash
        to track the state of the item's value. Validation is only performed if the
        state has changed or if the `force_live` parameter is set to True.

        Parameters:
        force_live (bool): If True, forces validation for LiveConfigItem instances
                        regardless of whether the state has changed. This is useful
                        when a new validator is added and immediate validation is required.

        Raises:
        ConfigItemValidationError: If any of the validators fail.
        """

        if isinstance(self, items.LiveConfigItem):

            current_value = self._get_value()

            state_hash = md5_hash_state(current_value)

            # Check if state has changed and we need to re-validate
            if not force_live and state_hash == self._last_state_hash:
                return  # We don't need to validate self or children
            else:
                self._last_state_hash = state_hash
        else:
            current_value = self.value

        self._validate_self(current_value)
        self._validate_children(current_value)

    def _validate_self(self, value):

        validate_value = value

        if potentially_has_children(value):
            validate_value = resolve_all_values(validate_value)

        for validator in self._validators:

            if not validator.validate(validate_value):
                raise ConfigItemValidationError(validator.error_message())

    def _validate_children(self, value):
        if isinstance(value, dict):

            for v in value.values():
                self._validate_value(v)

    def _validate_value(self, value):
        if isinstance(value, ValidatableMixin):
            value.validate()

    @property
    @abstractmethod
    def value(self) -> Any:
        pass
