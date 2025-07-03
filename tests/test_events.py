import unittest
import os
from unittest.mock import Mock, call
from fastcfg.config import Config
from fastcfg.sources.memory import from_os_environ
from fastcfg.config.events import ChangeEvent


class TestEventSystem(unittest.TestCase):
    """
    Test cases for the configuration event system.
    
    Tests the on_change decorator functionality for both static and live configuration items.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = Config(
            database={
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret"
                }
            },
            api={
                "base_url": "https://api.example.com",
                "timeout": 30
            }
        )
        
        # Set up environment variable for live config tests
        os.environ["TEST_DB_HOST"] = "initial.db.com"

    def tearDown(self):
        """Clean up after each test method."""
        if "TEST_DB_HOST" in os.environ:
            del os.environ["TEST_DB_HOST"]

    def test_on_change_decorator_basic(self):
        """Test basic on_change decorator functionality."""
        callback_called = []
        
        @self.config.database.host.on_change()
        def handle_host_change(event):
            callback_called.append(event)
        
        # Change the value
        self.config.database.host = "newhost.com"
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        
        # Verify event details
        event = callback_called[0]
        self.assertIsInstance(event, ChangeEvent)
        self.assertEqual(event.old_value, "localhost")
        self.assertEqual(event.new_value, "newhost.com")
        self.assertEqual(event.item, self.config.database.host._item)

    def test_on_change_direct_call(self):
        """Test on_change used as direct method call instead of decorator."""
        callback_mock = Mock()
        
        # Register callback directly
        self.config.database.port.on_change(callback_mock)
        
        # Change the value
        self.config.database.port = 3306
        
        # Verify callback was called
        callback_mock.assert_called_once()
        
        # Verify event details
        event = callback_mock.call_args[0][0]
        self.assertEqual(event.old_value, 5432)
        self.assertEqual(event.new_value, 3306)

    def test_on_change_multiple_listeners(self):
        """Test multiple listeners on the same configuration item."""
        callbacks_called = []
        
        @self.config.api.timeout.on_change()
        def handler1(event):
            callbacks_called.append(("handler1", event))
        
        @self.config.api.timeout.on_change()
        def handler2(event):
            callbacks_called.append(("handler2", event))
        
        # Change the value
        self.config.api.timeout = 60
        
        # Verify both callbacks were called
        self.assertEqual(len(callbacks_called), 2)
        self.assertEqual(callbacks_called[0][0], "handler1")
        self.assertEqual(callbacks_called[1][0], "handler2")
        
        # Both should have the same event data
        self.assertEqual(callbacks_called[0][1].old_value, 30)
        self.assertEqual(callbacks_called[1][1].old_value, 30)

    def test_on_change_nested_config(self):
        """Test on_change on nested configuration objects."""
        callback_called = []
        
        @self.config.database.credentials.username.on_change()
        def handle_username_change(event):
            callback_called.append(event)
        
        # Change nested value
        self.config.database.credentials.username = "newuser"
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, "admin")
        self.assertEqual(event.new_value, "newuser")

    def test_on_change_config_object_level(self):
        """Test on_change decorator on Config objects (not just leaf values)."""
        callback_called = []
        
        @self.config.database.on_change()  # Listen on database config
        def handle_database_change(event):
            callback_called.append(event)
        
        # Change any value in the database config
        self.config.database.host = "changed.com"
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, "localhost")
        self.assertEqual(event.new_value, "changed.com")

    def test_on_change_live_config_item(self):
        """Test on_change with LiveConfigItem that updates from external source."""
        # Create live config item
        self.config.live_host = from_os_environ("TEST_DB_HOST")
        
        callback_called = []
        
        @self.config.live_host.on_change()
        def handle_live_change(event):
            callback_called.append(event)
        
        # Access the value to establish baseline
        initial_value = self.config.live_host
        self.assertEqual(initial_value, "initial.db.com")
        
        # Change the environment variable
        os.environ["TEST_DB_HOST"] = "updated.db.com"
        
        # Access the value again to trigger change detection
        new_value = self.config.live_host.value
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, "initial.db.com")
        self.assertEqual(event.new_value, "updated.db.com")

    def test_on_change_no_duplicate_events(self):
        """Test that setting the same value doesn't trigger events."""
        callback_mock = Mock()
        
        self.config.database.host.on_change(callback_mock)
        
        # Set to the same value
        self.config.database.host = "localhost"
        
        # Should not trigger callback
        callback_mock.assert_not_called()

    def test_on_change_remove_listener(self):
        """Test removing event listeners."""
        callback_mock = Mock()
        
        # Add listener
        self.config.database.host.on_change(callback_mock)
        
        # Change value - should trigger
        self.config.database.host = "first.com"
        callback_mock.assert_called_once()
        
        # Remove listener
        self.config.database.host.remove_change_listener(callback_mock)
        
        # Change value again - should not trigger
        callback_mock.reset_mock()
        self.config.database.host = "second.com"
        callback_mock.assert_not_called()

    def test_on_change_event_object_properties(self):
        """Test that ChangeEvent object has all expected properties."""
        callback_called = []
        
        @self.config.database.port.on_change()
        def handle_change(event):
            callback_called.append(event)
        
        self.config.database.port = 8080
        
        event = callback_called[0]
        
        # Test all event properties
        self.assertIsInstance(event, ChangeEvent)
        self.assertEqual(event.old_value, 5432)
        self.assertEqual(event.new_value, 8080)
        self.assertIsNotNone(event.item)
        self.assertIsNotNone(event.timestamp)

    def test_on_change_with_environments(self):
        """Test on_change behavior with environment-specific configs."""
        env_config = Config(
            dev={"database": {"host": "dev.db.com"}},
            prod={"database": {"host": "prod.db.com"}}
        )
        
        env_config.set_environment("dev")
        
        callback_called = []
        
        @env_config.database.host.on_change()
        def handle_env_change(event):
            callback_called.append(event)
        
        # Change value in dev environment
        env_config.database.host = "newdev.db.com"
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, "dev.db.com")
        self.assertEqual(event.new_value, "newdev.db.com")
        
        # Switch to prod environment and change - should not trigger same listener
        callback_called.clear()
        env_config.set_environment("prod")
        env_config.database.host = "newprod.db.com"
        
        # Should not have triggered the dev listener
        self.assertEqual(len(callback_called), 0)

    def test_on_change_exception_handling(self):
        """Test that exceptions in one listener don't break others."""
        callback_called = []
        
        @self.config.database.host.on_change()
        def failing_handler(event):
            raise Exception("Handler failed!")
        
        @self.config.database.host.on_change()
        def working_handler(event):
            callback_called.append(event)
        
        # Change value - working handler should still be called despite failing one
        self.config.database.host = "test.com"
        
        # Verify working handler was called
        self.assertEqual(len(callback_called), 1)

    
    def test_on_change_method_chaining(self):
        """Test that on_change supports method chaining."""
        callback_mock = Mock()
        
        # Should be able to chain methods after on_change
        result = self.config.database.host.on_change(callback_mock)
        
        # on_change should return the callback for chaining
        self.assertEqual(result, callback_mock)

    def test_on_change_with_import_values(self):
        """Test that on_change triggers during import_values operations."""
        import tempfile
        import json
        
        callback_called = []
        
        @self.config.database.host.on_change()
        def handle_import_change(event):
            callback_called.append(event)
        
        # Create import data
        import_data = {
            "database": {
                "host": "imported.db.com"
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(import_data, f)
            temp_file = f.name
        
        try:
            # Import values
            self.config.import_values(temp_file)
            
            # Verify callback was triggered
            self.assertEqual(len(callback_called), 1)
            event = callback_called[0]
            self.assertEqual(event.old_value, "localhost")
            self.assertEqual(event.new_value, "imported.db.com")
        finally:
            os.unlink(temp_file)

    def test_on_change_with_update_method(self):
        """Test that on_change triggers during config.update() operations."""
        callback_called = []
        
        @self.config.api.timeout.on_change()
        def handle_update_change(event):
            callback_called.append(event)
        
        # Update config
        self.config.update({"api": {"timeout": 120}})
        
        # Verify callback was triggered
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, 30)
        self.assertEqual(event.new_value, 120)

    def test_on_change_direct_parent(self):
        """Test on_change on direct parent (one level up)."""
        callback_called = []
        
        # Listen on database config for changes to its children
        @self.config.database.on_change()
        def handle_database_change(event):
            callback_called.append(event)
        
        # Change a child of database
        self.config.database.host = "changed.com"
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, "localhost")
        self.assertEqual(event.new_value, "changed.com")
        # The item that changed should be the host item
        self.assertEqual(event.item, self.config.database.host._item)

    def test_on_change_grandparent(self):
        """Test on_change on grandparent (two levels up)."""
        callback_called = []
        
        # Listen on root config for changes to any descendant
        @self.config.on_change()
        def handle_root_change(event):
            callback_called.append(event)
        
        # Change a deeply nested value
        self.config.database.credentials.username = "newadmin"
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, "admin")
        self.assertEqual(event.new_value, "newadmin")
        # The item that changed should still be the username item
        self.assertEqual(event.item, self.config.database.credentials.username._item)

    def test_on_change_multiple_levels(self):
        """Test that all ancestors receive change events."""
        root_callbacks = []
        database_callbacks = []
        credentials_callbacks = []
        
        # Set up listeners at all levels
        @self.config.on_change()
        def handle_root(event):
            root_callbacks.append(("root", event))
        
        @self.config.database.on_change()
        def handle_database(event):
            database_callbacks.append(("database", event))
        
        @self.config.database.credentials.on_change()
        def handle_credentials(event):
            credentials_callbacks.append(("credentials", event))
        
        # Change the username
        self.config.database.credentials.username = "superadmin"
        
        # Verify all levels received the event
        self.assertEqual(len(credentials_callbacks), 1)
        self.assertEqual(len(database_callbacks), 1)
        self.assertEqual(len(root_callbacks), 1)
        
        # All should have the same event data
        for callbacks in [root_callbacks, database_callbacks, credentials_callbacks]:
            event = callbacks[0][1]
            self.assertEqual(event.old_value, "admin")
            self.assertEqual(event.new_value, "superadmin")
            self.assertEqual(event.item, self.config.database.credentials.username._item)

    def test_on_change_new_attribute_on_root(self):
        """Test on_change when adding a new attribute to root config."""
        callback_called = []
        
        @self.config.on_change()
        def handle_root_change(event):
            callback_called.append(event)
        
        # Add a new attribute to root
        self.config.new_setting = "new_value"
        
        # Root has no parent, so its own listener should not be triggered
        # (only parent listeners get notified, not self listeners)
        self.assertEqual(len(callback_called), 0)

    def test_on_change_sibling_isolation(self):
        """Test that sibling configs don't receive each other's events."""
        database_callbacks = []
        api_callbacks = []
        
        @self.config.database.on_change()
        def handle_database(event):
            database_callbacks.append(event)
        
        @self.config.api.on_change()
        def handle_api(event):
            api_callbacks.append(event)
        
        # Change something under api
        self.config.api.timeout = 60
        
        # Api should get notified of its child's change
        self.assertEqual(len(api_callbacks), 1)  # api DOES get its children's changes
        self.assertEqual(len(database_callbacks), 0)  # database doesn't get api changes
        
        # Verify the event details
        event = api_callbacks[0]
        self.assertEqual(event.old_value, 30)
        self.assertEqual(event.new_value, 60)

    def test_on_change_live_config_initial_access(self):
        """Test that LiveConfigItem fires event on first access after listener registration."""
        # Set up environment variable
        os.environ["TEST_INITIAL"] = "first_value"
        
        # Create live config item
        self.config.test_var = from_os_environ("TEST_INITIAL")
        
        callback_called = []
        
        # Register listener BEFORE first access
        @self.config.test_var.on_change()
        def handle_change(event):
            callback_called.append(event)
        
        # First access should fire event (None -> 'first_value')
        value = self.config.test_var.value
        self.assertEqual(value, "first_value")
        
        # Should have fired an event for the initial value
        self.assertEqual(len(callback_called), 1)
        event = callback_called[0]
        self.assertEqual(event.old_value, None)
        self.assertEqual(event.new_value, "first_value")
        
        # Clean up
        del os.environ["TEST_INITIAL"]

    def test_on_change_live_config_refresh_pattern(self):
        """Test that refresh pattern works correctly with LiveConfigItem."""
        # Import refresh function if available
        try:
            from fastcfg import refresh
        except ImportError:
            # Define a simple refresh function for the test
            def refresh(item):
                _ = item.value
        
        # Set up environment variable
        os.environ["TEST_REFRESH"] = "initial"
        
        # Create live config item
        self.config.refresh_var = from_os_environ("TEST_REFRESH")
        
        callback_called = []
        
        # Register listener
        @self.config.refresh_var.on_change()
        def handle_change(event):
            callback_called.append(event)
        
        # Initial access to establish baseline
        initial = self.config.refresh_var.value
        self.assertEqual(initial, "initial")
        
        # Change environment variable
        os.environ["TEST_REFRESH"] = "updated"
        
        # Use refresh to detect the change
        refresh(self.config.refresh_var)
        
        # Should have detected the change
        self.assertEqual(len(callback_called), 2)  # Initial None->initial, then initial->updated
        
        # Check the second event (the refresh-triggered one)
        event = callback_called[1]
        self.assertEqual(event.old_value, "initial")
        self.assertEqual(event.new_value, "updated")
        
        # Clean up
        del os.environ["TEST_REFRESH"]
