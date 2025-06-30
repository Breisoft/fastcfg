import tempfile
import unittest
import pickle
import json
import yaml
import os
from unittest.mock import Mock, patch
from unittest import skipIf

from fastcfg.config import Config
from fastcfg.sources.files import from_ini, from_json, from_yaml
from fastcfg.sources.memory import from_os_environ
from fastcfg.sources.aws import from_app_config


class TestSerialization(unittest.TestCase):
    """
    Test cases for Config serialization functionality.
    
    Tests the save, export_values, and load_values methods for different scenarios
    including full state serialization and value-only export/import.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = Config(
            database={
                "host": "prod.db.example.com",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret123"
                }
            },
            api={
                "base_url": "https://api.example.com",
                "timeout": 30,
                "retries": 3
            },
            cache={
                "enabled": True,
                "ttl": 3600
            }
        )

    def tearDown(self):
        """Clean up after each test method."""
        # Remove any temporary files created during tests
        for temp_file in getattr(self, '_temp_files', []):
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

    def _create_temp_file(self, suffix=''):
        """Helper method to create temporary files and track them for cleanup."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        if not hasattr(self, '_temp_files'):
            self._temp_files = []
        self._temp_files.append(temp_file.name)
        return temp_file.name

    def test_save_full_state_pickle(self):
        """
        Test saving full config state including live connections to pickle file.
        
        This should serialize the entire config object including all live connections,
        trackers, and internal state.
        """
        # Add some live connections to make the test more realistic
        self.config.live_db = from_os_environ("DATABASE_URL")
        self.config.live_api = from_app_config("my-app", "api-config")
        
        temp_file = self._create_temp_file('.pkl')
        
        # Save full state
        self.config.save(temp_file)
        
        # Verify file was created and contains pickle data
        self.assertTrue(os.path.exists(temp_file))
        self.assertGreater(os.path.getsize(temp_file), 0)
        
        # Load the saved state and verify it's identical
        with open(temp_file, 'rb') as f:
            loaded_config = pickle.load(f)
        
        # Verify the loaded config has the same structure and values
        self.assertEqual(loaded_config.database.host, "prod.db.example.com")
        self.assertEqual(loaded_config.database.port, 5432)
        self.assertEqual(loaded_config.api.base_url, "https://api.example.com")
        self.assertEqual(loaded_config.cache.enabled, True)
        
        # Verify live connections are preserved
        self.assertIsInstance(loaded_config.live_db, type(self.config.live_db))
        self.assertIsInstance(loaded_config.live_api, type(self.config.live_api))
    

    def test_save_full_state_with_environments(self):
        """
        Test saving full config state with environment-specific configurations.
        """
        # Create config with environments
        env_config = Config(
            dev={
                "database": {"host": "dev.db.example.com", "port": 5432},
                "api": {"base_url": "https://dev-api.example.com"}
            },
            prod={
                "database": {"host": "prod.db.example.com", "port": 5432},
                "api": {"base_url": "https://prod-api.example.com"}
            }
        )
        
        # Set active environment
        env_config.set_environment("dev")
        
        temp_file = self._create_temp_file('.pkl')
        
        # Save full state
        env_config.save(temp_file)
        
        # Load and verify environment state is preserved
        with open(temp_file, 'rb') as f:
            loaded_config = pickle.load(f)
        
        # Verify environment is preserved
        self.assertEqual(loaded_config.environment, "dev")
        self.assertEqual(loaded_config.database.host, "dev.db.example.com")
        
        # Switch environment and verify it works
        loaded_config.set_environment("prod")
        self.assertEqual(loaded_config.database.host, "prod.db.example.com")

    def test_export_values_json(self):
        """
        Test exporting only current values to JSON format.
        
        This should export only the resolved values without live connections
        or internal state, suitable for debugging and sharing.
        """
        temp_file = self._create_temp_file('.json')
        
        # Export values only
        self.config.export_values(temp_file)
        
        # Verify file was created and contains valid JSON
        self.assertTrue(os.path.exists(temp_file))
        
        with open(temp_file, 'r') as f:
            exported_data = json.load(f)
        
        # Verify the exported data contains only values (no live connections)
        expected_data = {
            "database": {
                "host": "prod.db.example.com",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret123"
                }
            },
            "api": {
                "base_url": "https://api.example.com",
                "timeout": 30,
                "retries": 3
            },
            "cache": {
                "enabled": True,
                "ttl": 3600
            }
        }
        
        self.assertEqual(exported_data, expected_data)

    def test_export_values_yaml(self):
        """
        Test exporting only current values to YAML format.
        """
        temp_file = self._create_temp_file('.yml')
        
        # Export values only
        self.config.export_values(temp_file)
        
        # Verify file was created and contains valid YAML
        self.assertTrue(os.path.exists(temp_file))
        
        with open(temp_file, 'r') as f:
            exported_data = yaml.safe_load(f)
        
        # Verify the exported data structure
        self.assertIn("database", exported_data)
        self.assertIn("api", exported_data)
        self.assertIn("cache", exported_data)
        self.assertEqual(exported_data["database"]["host"], "prod.db.example.com")

    def test_export_values_with_live_connections(self):
        """
        Test that export_values only exports resolved values, not live connections.
        """
        # Add live connections
        self.config.live_db = from_os_environ("DATABASE_URL")
        self.config.live_api = from_app_config("my-app", "api-config")
        
        temp_file = self._create_temp_file('.json')
        
        # Export values only
        self.config.export_values(temp_file)
        
        with open(temp_file, 'r') as f:
            exported_data = json.load(f)
        
        # Verify live connections are not in the exported data
        self.assertNotIn("live_db", exported_data)
        self.assertNotIn("live_api", exported_data)
        
        # Verify only static values are exported
        self.assertIn("database", exported_data)
        self.assertIn("api", exported_data)
        self.assertIn("cache", exported_data)

    def test_export_values_with_environments(self):
        """
        Test exporting values when an environment is active.
        """
        env_config = Config(
            dev={
                "database": {"host": "dev.db.example.com", "port": 5432},
                "api": {"base_url": "https://dev-api.example.com"}
            },
            prod={
                "database": {"host": "prod.db.example.com", "port": 5432},
                "api": {"base_url": "https://prod-api.example.com"}
            }
        )
        
        # Set active environment
        env_config.set_environment("dev")
        
        temp_file = self._create_temp_file('.json')
        
        # Export values only
        env_config.export_values(temp_file)
        
        with open(temp_file, 'r') as f:
            exported_data = json.load(f)
        
        # Should only export the active environment's values
        self.assertEqual(exported_data["database"]["host"], "dev.db.example.com")
        self.assertEqual(exported_data["api"]["base_url"], "https://dev-api.example.com")
        
        # Should not include environment structure
        self.assertNotIn("dev", exported_data)
        self.assertNotIn("prod", exported_data)

    def test_load_values_json(self):
        """
        Test loading static values from JSON file.
        
        This should create a new config with only static values, no live connections.
        """
        # Create a JSON file with static values
        static_data = {
            "database": {
                "host": "static.db.example.com",
                "port": 5432
            },
            "api": {
                "base_url": "https://static-api.example.com",
                "timeout": 60
            }
        }
        
        temp_file = self._create_temp_file('.json')
        with open(temp_file, 'w') as f:
            json.dump(static_data, f)
        
        # Load values into a new config
        new_config = Config()
        new_config.load_values(temp_file)
        
        # Verify the values were loaded correctly
        self.assertEqual(new_config.database.host, "static.db.example.com")
        self.assertEqual(new_config.database.port, 5432)
        self.assertEqual(new_config.api.base_url, "https://static-api.example.com")
        self.assertEqual(new_config.api.timeout, 60)

    def test_load_values_yaml(self):
        """
        Test loading static values from YAML file.
        """
        # Create a YAML file with static values
        static_data = {
            "database": {
                "host": "static.db.example.com",
                "port": 5432
            },
            "api": {
                "base_url": "https://static-api.example.com",
                "timeout": 60
            }
        }
        
        temp_file = self._create_temp_file('.yml')
        with open(temp_file, 'w') as f:
            yaml.dump(static_data, f)
        
        # Load values into a new config
        new_config = Config()
        new_config.load_values(temp_file)
        
        # Verify the values were loaded correctly
        self.assertEqual(new_config.database.host, "static.db.example.com")
        self.assertEqual(new_config.database.port, 5432)
        self.assertEqual(new_config.api.base_url, "https://static-api.example.com")
        self.assertEqual(new_config.api.timeout, 60)

    def test_load_values_into_existing_config(self):
        """
        Test loading values into an existing config, merging with existing values.
        """
        # Create existing config with some values
        existing_config = Config(
            existing_value="should_persist",
            database={"host": "existing.db.com", "port": 5432}
        )
        
        # Create a JSON file with new values
        new_data = {
            "database": {
                "host": "new.db.example.com",
                "port": 5433
            },
            "new_section": {
                "key": "value"
            }
        }
        
        temp_file = self._create_temp_file('.json')
        with open(temp_file, 'w') as f:
            json.dump(new_data, f)
        
        # Load values into existing config
        existing_config.load_values(temp_file)
        
        # Verify existing values persist
        self.assertEqual(existing_config.existing_value, "should_persist")
        
        # Verify new values are loaded
        self.assertEqual(existing_config.database.host, "new.db.example.com")
        self.assertEqual(existing_config.database.port, 5433)
        self.assertEqual(existing_config.new_section.key, "value")

    def test_save_with_validation(self):
        """
        Test that save preserves validation rules and validators.
        """
        from fastcfg.validation import RangeValidator
        
        # Add validation to config
        self.config.database.port.add_validator(RangeValidator(1, 65535))
        
        temp_file = self._create_temp_file('.pkl')
        
        # Save full state
        self.config.save(temp_file)
        
        # Load and verify validation is preserved
        with open(temp_file, 'rb') as f:
            loaded_config = pickle.load(f)
        
        # Verify validation still works
        self.assertEqual(loaded_config.database.port, 5432)  # Should pass validation
        
        # Verify validator is present
        self.assertTrue(hasattr(loaded_config.database.port, '_validators'))

    def test_export_values_file_format_detection(self):
        """
        Test that export_values automatically detects file format based on extension.
        """
        # Test JSON format
        json_file = self._create_temp_file('.json')
        self.config.export_values(json_file)
        
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        self.assertIsInstance(json_data, dict)
        
        # Test YAML format
        yaml_file = self._create_temp_file('.yml')
        self.config.export_values(yaml_file)
        
        with open(yaml_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        self.assertIsInstance(yaml_data, dict)

    def test_load_values_file_format_detection(self):
        """
        Test that load_values automatically detects file format based on extension.
        """
        test_data = {"key": "value", "number": 42}
        
        # Test JSON format
        json_file = self._create_temp_file('.json')
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        json_config = Config()
        json_config.load_values(json_file)
        self.assertEqual(json_config.key, "value")
        self.assertEqual(json_config.number, 42)
        
        # Test YAML format
        yaml_file = self._create_temp_file('.yml')
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        yaml_config = Config()
        yaml_config.load_values(yaml_file)
        self.assertEqual(yaml_config.key, "value")
        self.assertEqual(yaml_config.number, 42)

    def test_save_load_roundtrip(self):
        """
        Test that save and load work together for a complete roundtrip.
        """
        # Create config with various data types
        complex_config = Config(
            string_val="hello",
            int_val=42,
            float_val=3.14,
            bool_val=True,
            list_val=[1, 2, 3],
            dict_val={"a": 1, "b": 2},
            nested=Config(inner="value")
        )
        
        temp_file = self._create_temp_file('.pkl')
        
        # Save and load
        complex_config.save(temp_file)
        
        with open(temp_file, 'rb') as f:
            loaded_config = pickle.load(f)
        
        # Verify all values are preserved
        self.assertEqual(loaded_config.string_val, "hello")
        self.assertEqual(loaded_config.int_val, 42)
        self.assertEqual(loaded_config.float_val, 3.14)
        self.assertEqual(loaded_config.bool_val, True)
        self.assertEqual(loaded_config.list_val, [1, 2, 3])
        self.assertEqual(loaded_config.dict_val.a, 1)
        self.assertEqual(loaded_config.dict_val.b, 2)
        self.assertEqual(loaded_config.nested.inner, "value")

    def test_export_load_values_roundtrip(self):
        """
        Test that export_values and load_values work together for a complete roundtrip.
        """
        temp_file = self._create_temp_file('.json')
        
        # Export values
        self.config.export_values(temp_file)
        
        # Load values into new config
        new_config = Config()
        new_config.load_values(temp_file)
        
        # Verify values are preserved
        self.assertEqual(new_config.database.host, "prod.db.example.com")
        self.assertEqual(new_config.database.port, 5432)
        self.assertEqual(new_config.api.base_url, "https://api.example.com")
        self.assertEqual(new_config.cache.enabled, True)

    def test_save_invalid_file_path(self):
        """
        Test that save raises appropriate error for invalid file paths.
        """
        with self.assertRaises((OSError, IOError)):
            self.config.save("/invalid/path/that/does/not/exist/config.pkl")

    def test_export_values_invalid_file_path(self):
        """
        Test that export_values raises appropriate error for invalid file paths.
        """
        with self.assertRaises((OSError, IOError)):
            self.config.export_values("/invalid/path/that/does/not/exist/config.json")

    def test_load_values_invalid_file_path(self):
        """
        Test that load_values raises appropriate error for invalid file paths.
        """
        with self.assertRaises((OSError, IOError)):
            self.config.load_values("/invalid/path/that/does/not/exist/config.json")

    def test_load_values_invalid_json(self):
        """
        Test that load_values raises appropriate error for invalid JSON.
        """
        temp_file = self._create_temp_file('.json')
        with open(temp_file, 'w') as f:
            f.write('{"invalid": json}')
        
        with self.assertRaises((json.JSONDecodeError, ValueError)):
            self.config.load_values(temp_file)

    def test_load_values_invalid_yaml(self):
        """
        Test that load_values raises appropriate error for invalid YAML.
        """
        temp_file = self._create_temp_file('.yml')
        with open(temp_file, 'w') as f:
            f.write('invalid: yaml: content: [')
        
        with self.assertRaises((yaml.YAMLError, ValueError)):
            self.config.load_values(temp_file)

    def test_export_values_unsupported_format(self):
        """
        Test that export_values raises appropriate error for unsupported formats.
        """
        temp_file = self._create_temp_file('.txt')
        
        with self.assertRaises(ValueError):
            self.config.export_values(temp_file)

    def test_load_values_unsupported_format(self):
        """
        Test that load_values raises appropriate error for unsupported formats.
        """
        temp_file = self._create_temp_file('.txt')
        with open(temp_file, 'w') as f:
            f.write('some content')
        
        with self.assertRaises(ValueError):
            self.config.load_values(temp_file)

    @skipIf(not yaml, "PyYAML not available")
    def test_yaml_dependency_handling(self):
        """
        Test that YAML operations handle missing PyYAML dependency gracefully.
        """
        # This test should pass when PyYAML is available
        temp_file = self._create_temp_file('.yml')
        
        # Should work when PyYAML is available
        self.config.export_values(temp_file)
        
        with open(temp_file, 'r') as f:
            data = yaml.safe_load(f)
        self.assertIsInstance(data, dict)

    def test_save_with_complex_nested_structures(self):
        """
        Test saving config with complex nested structures including lists and mixed types.
        """
        complex_config = Config(
            servers=[
                {"host": "server1.com", "port": 8080},
                {"host": "server2.com", "port": 8081}
            ],
            settings={
                "timeout": 30,
                "retries": [1, 2, 3],
                "flags": {"debug": True, "verbose": False}
            },
            metadata={
                "version": "1.0.0",
                "tags": ["production", "stable"]
            }
        )
        
        temp_file = self._create_temp_file('.pkl')
        
        # Save full state
        complex_config.save(temp_file)
        
        # Load and verify complex structures
        with open(temp_file, 'rb') as f:
            loaded_config = pickle.load(f)
        
        # Verify nested structures are preserved
        self.assertEqual(len(loaded_config.servers), 2)
        self.assertEqual(loaded_config.servers[0].host, "server1.com")
        self.assertEqual(loaded_config.servers[1].port, 8081)
        
        self.assertEqual(loaded_config.settings.timeout, 30)
        self.assertEqual(loaded_config.settings.retries, [1, 2, 3])
        self.assertEqual(loaded_config.settings.flags.debug, True)
        
        self.assertEqual(loaded_config.metadata.version, "1.0.0")
        self.assertEqual(loaded_config.metadata.tags, ["production", "stable"])

    def test_export_values_with_complex_nested_structures(self):
        """
        Test exporting values with complex nested structures.
        """
        complex_config = Config(
            servers=[
                {"host": "server1.com", "port": 8080},
                {"host": "server2.com", "port": 8081}
            ],
            settings={
                "timeout": 30,
                "retries": [1, 2, 3],
                "flags": {"debug": True, "verbose": False}
            }
        )
        
        temp_file = self._create_temp_file('.json')
        
        # Export values
        complex_config.export_values(temp_file)
        
        with open(temp_file, 'r') as f:
            exported_data = json.load(f)
        
        # Verify complex structures are exported correctly
        self.assertEqual(len(exported_data["servers"]), 2)
        self.assertEqual(exported_data["servers"][0]["host"], "server1.com")
        self.assertEqual(exported_data["servers"][1]["port"], 8081)
        
        self.assertEqual(exported_data["settings"]["timeout"], 30)
        self.assertEqual(exported_data["settings"]["retries"], [1, 2, 3])
        self.assertEqual(exported_data["settings"]["flags"]["debug"], True)
        self.assertEqual(exported_data["settings"]["flags"]["verbose"], False)
