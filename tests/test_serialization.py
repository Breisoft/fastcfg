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