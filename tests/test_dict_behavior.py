import unittest
from unittest.mock import Mock

from fastcfg import Config
from fastcfg.config.items import LiveConfigItem


class TestDictBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config(
            data=Config(
                data={
                    "data": {
                        "a": 1,
                        "b": 2,
                        "c": 3,
                    }
                }
            )
        )

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

    def test_dict_behavior_with_nested_config(self):
        self.assertEqual(self.config.to_dict(),
                        {
                            "data": {
                                "data": {
                                    "data": {
                                        "a": 1,
                                        "b": 2,
                                        "c": 3,
                                    }
                                }
                            }
                        })
        
    def test_dict_function(self):
        """Test the dict() function works as expected"""
        
        self.assertEqual(self.config.to_dict(), dict(self.config))


    def test_items_and_keys_and_values(self):
        """Test the items(), keys(), and values() methods work as expected"""
        
        for k, v in self.config.items():
            pass
        
        for k in self.config.keys():
            pass
        
        for v in self.config.values():
            pass
        
