import tempfile
import unittest
from unittest import skipIf

from fastcfg.config import Config
from fastcfg.sources.files import from_ini, from_json, from_yaml

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class TestFileSources(unittest.TestCase):

    @skipIf(not YAML_AVAILABLE, "YAML library not available")
    def test_yaml(self):
        """
        Test the YAML source
        """

        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile("w+") as temp_yaml:
            yaml.dump({"key": "value"}, temp_yaml)
            temp_yaml.seek(0)

            config = Config()
            config.yaml = from_yaml(temp_yaml.name)

            self.assertEqual(config.yaml, {"key": "value"})
            self.assertEqual(config.yaml.key, "value")

    def test_json(self):
        """
        Test the JSON source
        """

        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile("w+") as temp_json:
            temp_json.write('{"key": "value"}')
            temp_json.seek(0)

            config = Config()
            config.json = from_json(temp_json.name)

            self.assertEqual(config.json, {"key": "value"})
            self.assertEqual(config.json.key, "value")

    # TODO uncomment
    """
    def test_ini(self):


        # Create a temporary INI file
        with tempfile.NamedTemporaryFile('w+') as temp_ini:
            temp_ini.write("[section]\nkey=value")
            temp_ini.seek(0)

            config = Config()
            config.ini = from_ini(temp_ini.name)

            self.assertEqual(config.ini, {"section": {"key": "value"}})

            self.assertEqual(config.ini.section.key, 'value')
    """
