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
from fastcfg.config.items import BuiltInConfigItem, LiveConfigItem
from fastcfg.sources.files import from_yaml
import tempfile

import time


try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def tearDown(self):
        self.config = None

    def _trigger_access(self, item):
        # Access the value property directly to trigger validation
        _ = str(item)

    def test_invoke_does_not_call_validation_for_builtin(self):
        """Validation should not be invoked on access for a BuiltInConfig"""
        # Create a real BuiltInConfigItem
        item = BuiltInConfigItem("mock_value")
        self.config.xyz = item

        validator_mock = MagicMock()
        validator_mock.validate_immediately = False  # Set validate_immediately to False
        validator_mock.validate = MagicMock()  # Explicitly define the validate method
        item.add_validator(validator_mock)

        self._trigger_access(self.config.xyz)

        validator_mock.validate.assert_not_called()

    def test_invoke_calls_validation_for_liveconfigitem(self):
        # Mock state tracker with a callable that returns the current time
        state_tracker = MagicMock()
        state_tracker.get_state = MagicMock(side_effect=lambda: time.time())

        # Create a LiveConfigItem
        item = LiveConfigItem(state_tracker)

        validator_mock = MagicMock()
        validator_mock.validate_immediately = False  # Set validate_immediately to False
        validator_mock.validate = MagicMock()  # Explicitly define the validate method
        item.add_validator(validator_mock)

        validator_mock.validate.assert_not_called()

        # Assign the LiveConfigItem to the config
        self.config.xyz = item

        # Trigger validation by accessing the value
        self._trigger_access(self.config.xyz)

        validator_mock.validate.assert_called()

        # Trigger validation again by accessing the value (state will change)
        time.sleep(0.1)  # Ensure the time changes
        self._trigger_access(self.config.xyz)

        # Validate should be called again due to state change
        print('State change detected, call count:',
              validator_mock.validate.call_count)
        self.assertGreaterEqual(validator_mock.validate.call_count, 2)

    def test_type_validator(self):
        self.config.int_value = 42
        self.config.int_value.add_validator(TypeValidator(int))
        self._trigger_access(self.config.int_value)

        self.config.str_value = "hello"
        self.config.str_value.add_validator(TypeValidator(str))
        self._trigger_access(self.config.str_value)

        self.config.invalid_value = 42

        with self.assertRaises(ConfigItemValidationError):
            self.config.invalid_value.add_validator(TypeValidator(str))

    def test_range_validator_in_range(self):
        self.config.numeric = 5

        self.config.numeric.add_validator(RangeValidator(1, 6))

        self._trigger_access(self.config.numeric)

    def test_range_validator_outside_range(self):
        self.config.numeric = 0

        with self.assertRaises(ConfigItemValidationError):
            self.config.numeric.add_validator(RangeValidator(1, 6))

    def test_range_validator_inclusive_start(self):

        two_to_four_val = RangeValidator(2, 4)

        self.config.start_range = 2

        self.config.start_range.add_validator(two_to_four_val)

        self._trigger_access(self.config.start_range)

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
        self._trigger_access(self.config.email)

        self.config.invalid_email = "invalid-email"

        with self.assertRaises(ConfigItemValidationError):
            self.config.invalid_email.add_validator(
                RegexValidator(r"^[\w\.-]+@[\w\.-]+\.\w+$"))

    def test_add_validator_to_dict(self):
        self.config.nested = {"key": "value"}
        self.config.nested.add_validator(TypeValidator(dict))
        self._trigger_access(self.config.nested)

        self.config.nested.key.add_validator(TypeValidator(str))
        self._trigger_access(self.config.nested.key)

        self.config.invalid_nested = 42

        with self.assertRaises(ConfigItemValidationError):
            self.config.invalid_nested.add_validator(TypeValidator(dict))

    @unittest.skipIf(not PYDANTIC_AVAILABLE, "pydantic is not installed")
    def test_invalid_pydantic_value(self):
        class UserModel(BaseModel):
            name: str
            age: int

        import yaml

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile('w+') as temp_yaml:
            yaml.dump({"name": "John", "age": "abc"}, temp_yaml)
            temp_yaml.seek(0)

            self.config.invalid_user = from_yaml(temp_yaml.name)

            validator = PydanticValidator(UserModel)

            # Trigger validation by accessing the value
            with self.assertRaises(ConfigItemValidationError):
                self.config.invalid_user.add_validator(validator)

    @ unittest.skipIf(not PYDANTIC_AVAILABLE, "pydantic is not installed")
    def test_pydantic_validator(self):
        class UserModel(BaseModel):
            name: str
            age: int

        import yaml

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile('w+') as temp_yaml:
            yaml.dump({"name": "John", "age": 30}, temp_yaml)
            temp_yaml.seek(0)

            self.config.user = from_yaml(temp_yaml.name)

            self.config.user.add_validator(PydanticValidator(UserModel))

            # Should not raise a ConfigItemValidationError exception
            self._trigger_access(self.config.user)

    @ unittest.skipIf(not PYDANTIC_AVAILABLE, "pydantic is not installed")
    def test_multi_validator(self):
        class UserModel(BaseModel):
            name: str
            age: int

        import yaml

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile('w+') as temp_yaml:
            yaml.dump({"name": "John", "age": 29}, temp_yaml)
            temp_yaml.seek(0)

            self.config.user = from_yaml(temp_yaml.name)

            # Should not raise a ConfigItemValidationError exception
            self.config.user.add_validator(PydanticValidator(UserModel))

            # Should raise a ConfigItemValidationError exception
            with self.assertRaises(ConfigItemValidationError):
                self.config.user.age.add_validator(RangeValidator(30, 35))

    def test_input_pydantic_validation(self):

        class User(BaseModel):
            name: str
            age: int

        config = Config(user={'name': 'Steve', 'age': 'abc'})

        with self.assertRaises(ConfigItemValidationError):
            config.user.add_validator(PydanticValidator(User))

    def test_lazy_validation_multiple_changes(self):
        config = Config(int_val=None)

        lazy_range_validator = RangeValidator(
            15, 20, validate_immediately=False)

        # Should not raise ConfigItemValidationError exception when adding the validator
        config.int_val.add_validator(lazy_range_validator)

        # Should not raise an exception for a valid value within the range
        config.int_val = 18

        # Should raise an exception for an invalid value outside the range
        with self.assertRaises(ConfigItemValidationError):
            config.int_val = 21

        # Should not raise an exception for another valid value within the range
        config.int_val = 17

        # Should raise an exception for another invalid value outside the range
        with self.assertRaises(ConfigItemValidationError):
            config.int_val = 14

    def test_immediate_validation(self):

        config = Config(int_val=None)

        immediate_range_validator = RangeValidator(
            15, 20, validate_immediately=True)

        # Should not raise ConfigItemValidationError exception
        with self.assertRaises(ConfigItemValidationError):
            config.int_val.add_validator(immediate_range_validator)
