import unittest
from unittest.mock import MagicMock, patch


from fastcfg.config import Config
from fastcfg.validation.policies import (
    RangeValidator,
    RegexValidator,
    PydanticValidator,
    TypeValidator
)
from fastcfg.exceptions import ConfigItemValidationError
from fastcfg.config.items import BuiltInConfigItem
from fastcfg.sources.memory import from_yaml
import tempfile


try:
    from pydantic import BaseModel, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def tearDown(self):
        self.config = None

    def _trigger_validation(self, item):
        # Access the value property directly to trigger validation
        _ = str(item)

    def test_invoke_calls_validation(self):
        # Create a real BuiltInConfigItem
        item = BuiltInConfigItem("mock_value")
        item.validate = MagicMock()

        self.config.xyz = item

        self._trigger_validation(self.config.xyz)

        item.validate.assert_called_once_with("mock_value")

    def test_type_validator(self):
        self.config.int_value = 42
        self.config.int_value.add_validator(TypeValidator(int))
        self._trigger_validation(self.config.int_value)

        self.config.str_value = "hello"
        self.config.str_value.add_validator(TypeValidator(str))
        self._trigger_validation(self.config.str_value)

        self.config.invalid_value = 42
        self.config.invalid_value.add_validator(TypeValidator(str))
        with self.assertRaises(ConfigItemValidationError):
            self._trigger_validation(self.config.invalid_value)

    def test_range_validator_in_range(self):
        self.config.numeric = 5

        self.config.numeric.add_validator(RangeValidator(1, 6))

        self._trigger_validation(self.config.numeric)

    def test_range_validator_outside_range(self):
        self.config.numeric = 0

        self.config.numeric.add_validator(RangeValidator(1, 6))

        with self.assertRaises(ConfigItemValidationError):
            self._trigger_validation(self.config.numeric)

    def test_range_validator_inclusive_start(self):

        two_to_four_val = RangeValidator(2, 4)

        self.config.start_range = 2

        self.config.start_range.add_validator(two_to_four_val)

        self._trigger_validation(self.config.start_range)

    def test_range_validator_inclusive_end(self):

        two_to_four_val = RangeValidator(2, 4)

        self.config.end_range = 4

        self.config.end_range.add_validator(two_to_four_val)

        str(self.config.end_range)

    def test_regex_validator(self):
        self.config.email = "test@example.com"
        self.config.email.add_validator(
            RegexValidator(r"^[\w\.-]+@[\w\.-]+\.\w+$"))

        # Should not raise a ConfigItemValidationError exception
        self._trigger_validation(self.config.email)

        self.config.invalid_email = "invalid-email"
        self.config.invalid_email.add_validator(
            RegexValidator(r"^[\w\.-]+@[\w\.-]+\.\w+$"))

        with self.assertRaises(ConfigItemValidationError):
            self._trigger_validation(self.config.invalid_email)

    # TODO add this back
    """
    @unittest.skipIf(not PYDANTIC_AVAILABLE, "pydantic is not installed")
    def test_pydantic_validator(self):
        class UserModel(BaseModel):
            name: str
            age: int

        import yaml

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile('w+', delete=False) as temp_yaml:
            yaml.dump({"name": "John", "age": 30}, temp_yaml)
            temp_yaml.seek(0)

            self.config.user = from_yaml(temp_yaml.name)

            self.config.user.add_validator(PydanticValidator(UserModel))

            # Should not raise a ConfigItemValidationError exception
            str(self.config.user)

        # Should not raise a ConfigItemValidationError exception
        str(self.config.user)

        self.config.invalid_user = {"name": "John", "age": "thirty"}
        self.config.invalid_user.add_validator(PydanticValidator(UserModel))

        with self.assertRaises(ConfigItemValidationError):
            str(self.config.invalid_user)
    """
