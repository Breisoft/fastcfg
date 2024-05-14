from unittest import mock
import unittest
from fastcfg.config import Config
from fastcfg.sources.local import from_yaml
import os


class TestFileSources(unittest.TestCase):
    pass
    """

    def test_real_file(self):
        # Create a temporary yaml file for testing
        with open("fastcfg_temp_config.yaml", "w") as f:
            f.write("key: value")

        # Load the yaml file as a config source
        config = Config()
        config.test_yml = from_yaml("fastcfg_temp_config.yaml")

        # Check that the value is loaded correctly
        self.assertEqual(config.test_yml.get("key"), "value")

        # Delete the temporary yaml file
        os.remove("temp_config.yaml")

        # Check that the file was deleted
        self.assertFalse(os.path.exists("temp_config.yaml"))
    """
