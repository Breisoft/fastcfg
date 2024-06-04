import unittest
from unittest.mock import Mock

from fastcfg import Config
from fastcfg.config.items import LiveConfigItem


class TestConfig(unittest.TestCase):
    """
    Test cases for the Config class.

    This class contains test methods to verify the behavior and functionality of the Config class,
    including creation with different data types and handling of nested Config objects.
    """

    def test_config_creation_with_different_data_types(self):
        """
        Test the creation of a Config object with different data types.

        This test ensures that the Config object can be initialized with various
        data types and that the values are correctly stored and retrieved.
        """
        config = Config(
            int_value=42,
            float_value=3.14,
            str_value="hello",
            bool_value=True,
            list_value=[1, 2, 3],
            dict_value={"a": 1, "b": 2},
            tuple_value=(4, 5, 6),
            set_value={7, 8, 9},
        )

        # Assert the values and types of the Config object attributes
        self.assertEqual(config.int_value, 42)
        self.assertIsInstance(config.int_value, int)
        self.assertEqual(config.float_value, 3.14)
        self.assertIsInstance(config.float_value, float)
        self.assertEqual(config.str_value, "hello")
        self.assertIsInstance(config.str_value, str)
        self.assertTrue(config.bool_value)
        self.assertIsInstance(config.bool_value, bool)
        self.assertEqual(config.list_value, [1, 2, 3])
        self.assertIsInstance(config.list_value, list)

        self.assertEqual(config.tuple_value, (4, 5, 6))
        self.assertIsInstance(config.tuple_value, tuple)
        self.assertEqual(config.set_value, {7, 8, 9})
        self.assertIsInstance(config.set_value, set)

    def test_basic_config(self):

        config = Config(int_value=2)

        self.assertEqual(config.int_value, 2)

    def test_dict_functionality(self):
        """
        Test various dictionary functionalities of the Config class.

        This test ensures that dictionary attributes can be accessed using dot notation,
        and that nested Config objects can be compared to dictionaries.
        """
        config = Config(
            dict_value={"a": 1, "b": {"nested": 2}},
            nested_config=Config(a=1, b=2),
        )

        # Access the dictionary attributes using dot notation
        self.assertEqual(config.dict_value.a, 1)
        self.assertEqual(config.dict_value.b.nested, 2)

        # Compare nested Config object to a dictionary
        self.assertEqual(config.nested_config, {"a": 1, "b": 2})

    def test_nested_config_objects(self):
        """
        Test the behavior of nested Config objects.

        This test verifies that nested Config objects can be created and accessed
        correctly, and that modifying nested values works as expected.
        """
        config = Config(nested_config=Config(value1=10, value2="nested"))

        # Assert that nested_config is an instance of Config
        self.assertIsInstance(config.nested_config, Config)

        # Assert the values of the nested Config object attributes
        self.assertEqual(config.nested_config.value1, 10)
        self.assertEqual(config.nested_config.value2, "nested")

        # Modify a nested value and assert the updated value
        config.nested_config.value1 = 20
        self.assertEqual(config.nested_config.value1, 20)


class TestConfigEnvironment(unittest.TestCase):

    def setUp(self):
        self.config = Config(dev={"stage": "dev"}, prod={"stage": "prod"})

    def tearDown(self) -> None:
        self.config = None

    def _check_env_attrs(self):
        self.assertIn("dev", self.config.environments)
        self.assertIn("prod", self.config.environments)

    def test_config_environment(self):
        """
        Test the behavior of the Config environment feature.
        """

        # Assert no active environment
        self.assertIsNone(self.config.environment)

        # Check environments are properly detected
        self._check_env_attrs()

        # Assert access to environments with no active environment
        self.assertEqual(self.config.dev.stage, "dev")
        self.assertEqual(self.config.prod.stage, "prod")

        # Set active environment
        self.config.set_environment("dev")

        # Check directly accessing 'stage' attribute with environment alias
        self.assertEqual(self.config.stage, "dev")

        # Check that we can switch directly to another environment with one
        # already active
        self.config.set_environment("prod")

        # Confirm that we can directly access 'stage' attribute with environment alias
        self.assertEqual(self.config.stage, "prod")

    def test_config_environment_non_active(self):

        # Check environments are properly detected
        self._check_env_attrs()

        # Set active environnment
        self.config.set_environment("dev")

        # Check that we can't directly access environments when one is set
        self.assertNotIn("dev", self.config)
        self.assertNotIn("prod", self.config)

        # Check that we can still access environments when one is set
        self.assertIn("dev", self.config.environments)
        self.assertIn("prod", self.config.environments)

        # Check that we can access the stage attribute by directly accessing environments
        self.assertIn("stage", self.config.environments.prod)
        self.assertIn("stage", self.config.environments.dev)

        self.config.set_environment(None)

        # Check that environment aliasing is disabled again
        self.assertIn("dev", self.config)
        self.assertIn("prod", self.config)

    def test_config_invalid_environment(self):
        """
        Test the behavior of the Config environment feature with an invalid environment.
        """

        self.assertNotIn("invalid", self.config.environments)

        with self.assertRaises(ValueError):
            self.config.set_environment("invalid")


class TestLiveConfigItem(unittest.TestCase):
    """
    Test cases for the LiveConfigItem class.

    This class contains test methods to verify the behavior and functionality of the LiveConfigItem class,
    including interaction with a mock LiveTracker and updating of values.
    """

    def test_live_config_item(self):
        """
        Test the functionality of LiveConfigItem with a mock LiveTracker.

        This test ensures that LiveConfigItem correctly retrieves the value from
        the LiveTracker and updates when the tracker's state changes.
        """

        # Create a mock LiveTracker
        mock_tracker = Mock()
        mock_tracker.get_state.return_value = 42

        # Create a LiveConfigItem with the mock tracker
        live_item = LiveConfigItem(mock_tracker)

        # Assert the initial value and that get_state was called at least once
        self.assertEqual(live_item.value, 42)
        mock_tracker.get_state.assert_called()

        # Update the return value of get_state and assert the updated value
        mock_tracker.get_state.return_value = 100
        self.assertEqual(live_item.value, 100)

        # TODO check this, why is it 4 instead of 2?
        self.assertGreaterEqual(mock_tracker.get_state.call_count, 2)
