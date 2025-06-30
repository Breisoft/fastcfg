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

        os.environ["DATABASE_URL"] = "prod.db.example.com"

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
        # self.config.live_api = from_app_config("my-app", "api-config")
        
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
        # self.assertIsInstance(loaded_config.live_api,
        # type(self.config.live_api))
        
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

    def test_import_values_json(self):
        """
        Test importing configuration values from JSON format.
        
        This should import values and update the existing configuration
        without affecting live connections or internal state.
        """
        # Create a new config with minimal initial values
        import_config = Config(
            database={
                "host": "initial.db.example.com",
                "port": 3306
            },
            api={
                "base_url": "https://initial-api.example.com"
            }
        )
        
        # Create JSON file with new values to import
        import_data = {
            "database": {
                "host": "imported.db.example.com",
                "port": 5432,
                "credentials": {
                    "username": "imported_user",
                    "password": "imported_pass"
                }
            },
            "api": {
                "base_url": "https://imported-api.example.com",
                "timeout": 60,
                "retries": 5
            },
            "new_section": {
                "feature_flag": True,
                "max_connections": 100
            }
        }
        
        temp_file = self._create_temp_file('.json')
        
        # Write the import data to the file
        with open(temp_file, 'w') as f:
            json.dump(import_data, f)
        
        # Import the values
        import_config.import_values(temp_file)
        
        # Verify the imported values are correctly applied
        self.assertEqual(import_config.database.host, "imported.db.example.com")
        self.assertEqual(import_config.database.port, 5432)
        self.assertEqual(import_config.database.credentials.username, "imported_user")
        self.assertEqual(import_config.database.credentials.password, "imported_pass")
        
        self.assertEqual(import_config.api.base_url, "https://imported-api.example.com")
        self.assertEqual(import_config.api.timeout, 60)
        self.assertEqual(import_config.api.retries, 5)
        
        # Verify new sections are added
        self.assertEqual(import_config.new_section.feature_flag, True)
        self.assertEqual(import_config.new_section.max_connections, 100)

    def test_import_values_yaml(self):
        """
        Test importing configuration values from YAML format.
        """
        # Create a new config with minimal initial values
        import_config = Config(
            database={
                "host": "initial.db.example.com"
            }
        )
        
        # Create YAML file with new values to import
        import_data = {
            "database": {
                "host": "yaml-imported.db.example.com",
                "port": 8080
            },
            "logging": {
                "level": "DEBUG",
                "format": "json"
            }
        }
        
        temp_file = self._create_temp_file('.yaml')
        
        # Write the import data to the file
        with open(temp_file, 'w') as f:
            yaml.dump(import_data, f)
        
        # Import the values
        import_config.import_values(temp_file)
        
        # Verify the imported values are correctly applied
        self.assertEqual(import_config.database.host, "yaml-imported.db.example.com")
        self.assertEqual(import_config.database.port, 8080)
        self.assertEqual(import_config.logging.level, "DEBUG")
        self.assertEqual(import_config.logging.format, "json")

    def test_import_values_with_environments(self):
        """
        Test importing values when using environment-specific configurations.
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
        
        # Create import data
        import_data = {
            "database": {
                "host": "imported-dev.db.example.com",
                "port": 3306
            },
            "api": {
                "base_url": "https://imported-dev-api.example.com",
                "timeout": 45
            }
        }
        
        temp_file = self._create_temp_file('.json')
        
        # Write the import data to the file
        with open(temp_file, 'w') as f:
            json.dump(import_data, f)
        
        # Import the values
        env_config.import_values(temp_file)
        
        # Verify the imported values are correctly applied to the current environment
        self.assertEqual(env_config.database.host, "imported-dev.db.example.com")
        self.assertEqual(env_config.database.port, 3306)
        self.assertEqual(env_config.api.base_url, "https://imported-dev-api.example.com")
        self.assertEqual(env_config.api.timeout, 45)
        
        # Switch to prod environment and verify it's unchanged
        env_config.set_environment("prod")
        self.assertEqual(env_config.database.host, "prod.db.example.com")
        self.assertEqual(env_config.api.base_url, "https://prod-api.example.com")

    def test_import_values_partial_update(self):
        """
        Test importing values that only update some existing fields.
        """
        # Create config with existing values
        config = Config(
            database={
                "host": "existing.db.example.com",
                "port": 5432,
                "credentials": {
                    "username": "existing_user",
                    "password": "existing_pass"
                }
            },
            api={
                "base_url": "https://existing-api.example.com",
                "timeout": 30
            }
        )
        
        # Create import data that only updates some fields
        import_data = {
            "database": {
                "host": "updated.db.example.com",
                "credentials": {
                    "password": "updated_pass"
                }
            },
            "api": {
                "timeout": 60
            }
        }
        
        temp_file = self._create_temp_file('.json')
        
        # Write the import data to the file
        with open(temp_file, 'w') as f:
            json.dump(import_data, f)
        
        # Import the values
        config.import_values(temp_file)
        
        # Verify updated fields are changed
        self.assertEqual(config.database.host, "updated.db.example.com")
        self.assertEqual(config.database.credentials.password, "updated_pass")
        self.assertEqual(config.api.timeout, 60)
        
        # Verify unchanged fields remain the same
        # Note: Dictionaries are converted to Config objects, so we can access them as attributes
        self.assertEqual(config.database.port, 5432)
        self.assertEqual(config.database.credentials.username, "existing_user")
        self.assertEqual(config.api.base_url, "https://existing-api.example.com")

    def test_import_values_file_not_found(self):
        """
        Test that import_values raises an appropriate error when file doesn't exist.
        """
        config = Config()
        
        # Try to import from a non-existent file
        with self.assertRaises(FileNotFoundError):
            config.import_values("non_existent_file.json")

    def test_import_values_invalid_json(self):
        """
        Test that import_values handles invalid JSON gracefully.
        """
        config = Config()
        
        # Create a file with invalid JSON
        temp_file = self._create_temp_file('.json')
        with open(temp_file, 'w') as f:
            f.write('{"invalid": json}')
        
        # Try to import invalid JSON
        with self.assertRaises(json.JSONDecodeError):
            config.import_values(temp_file)

    def test_import_values_deep_merge_edge_cases(self):
        """Test edge cases in deep merge behavior."""
        config = Config(
            nested={
                "level1": {
                    "level2": {
                        "existing": "value",
                        "to_replace": "old"
                    }
                }
            }
        )
        
        import_data = {
            "nested": {
                "level1": {
                    "level2": {
                        "to_replace": "new",
                        "added": "fresh"
                    }
                }
            }
        }
        
        # Test 3-level deep merge
        temp_file = self._create_temp_file('.json')
        with open(temp_file, 'w') as f:
            json.dump(import_data, f)
        config.import_values(temp_file)
        self.assertEqual(config.nested.level1.level2.existing, "value")  # preserved
        self.assertEqual(config.nested.level1.level2.to_replace, "new")  # updated
        self.assertEqual(config.nested.level1.level2.added, "fresh")     # added