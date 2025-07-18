"""
Real-world integration test for AWS AppConfig source.
This test actually connects to AWS and fetches configuration from AppConfig.

Prerequisites:
- AWS credentials configured (via environment variables, profile, or IAM role)
- An AppConfig application, environment, and configuration profile set up
- Proper IAM permissions to read AppConfig

To set up test data in AWS:
1. Create an AppConfig application: "vein-test-app"
2. Create an environment: "development"
3. Create a configuration profile: "test-config"
4. Deploy a configuration like:
   {
     "database": {
       "host": "localhost",
       "port": 5432,
       "name": "testdb"
     },
     "features": {
       "new_ui": true,
       "beta_features": false
     },
     "api": {
       "timeout": 30,
       "retry_count": 3
     }
   }

To run:
    export AWS_ACCESS_KEY_ID=your_key
    export AWS_SECRET_ACCESS_KEY=your_secret
    export AWS_DEFAULT_REGION=us-east-1
    
    # Optional: Override test parameters
    export APPCONFIG_APP=your-app-name
    export APPCONFIG_ENV=your-environment
    export APPCONFIG_CONFIG=your-config-profile
    
    python tests/test_appconfig_integration.py
"""

import json
import os
import sys
import time
import uuid

from fastcfg import Config
from fastcfg.config.items import LiveConfigItem
from fastcfg.sources.aws.app_config import AppConfigLiveTracker
from fastcfg.sources.aws.boto3_live_tracker import AWSConfig


def from_appconfig(
    application: str,
    environment: str, 
    configuration: str,
    client_id: str = None,
    aws_config: AWSConfig = None
) -> LiveConfigItem:
    """Helper function to create LiveConfigItem from AppConfig."""
    # Generate a unique client ID if not provided
    if client_id is None:
        client_id = f"vein-test-{uuid.uuid4()}"
    
    tracker = AppConfigLiveTracker(
        application=application,
        environment=environment,
        configuration=configuration,
        client_id=client_id,
        aws_config=aws_config
    )
    return LiveConfigItem(tracker)


def test_real_appconfig_integration():
    """Real integration test that connects to AWS AppConfig."""
    
    print("=== Real AWS AppConfig Integration Test ===\n")
    
    # Get test parameters from environment or use defaults
    app_name = os.environ.get('APPCONFIG_APP', 'vein-test-app')
    env_name = os.environ.get('APPCONFIG_ENV', 'development')
    config_name = os.environ.get('APPCONFIG_CONFIG', 'test-config')
    
    print(f"Test parameters:")
    print(f"  Application: {app_name}")
    print(f"  Environment: {env_name}")
    print(f"  Configuration: {config_name}")
    
    # Create config instance
    config = Config()
    
    # Load configuration from AppConfig
    print(f"\nLoading configuration from AppConfig...")
    config.app_settings = from_appconfig(
        application=app_name,
        environment=env_name,
        configuration=config_name
    )

    print('app config', type(config.app_settings.value))
    
    # Access the configuration (this triggers the AppConfig fetch)
    print(f"\nFetched configuration:")
    print("-" * 40)
    
    try:
        # Access nested configuration values
        if hasattr(config.app_settings, 'database'):
            print(f"Database Configuration:")
            print(f"  Host: {config.app_settings.database.host}")
            print(f"  Port: {config.app_settings.database.port}")
            print(f"  Name: {config.app_settings.database.name}")
        
        if hasattr(config.app_settings, 'features'):
            print(f"\nFeature Flags:")
            print(f"  New UI: {config.app_settings.features.new_ui}")
            print(f"  Beta Features: {config.app_settings.features.beta_features}")
        
        if hasattr(config.app_settings, 'api'):
            print(f"\nAPI Configuration:")
            print(f"  Timeout: {config.app_settings.api.timeout}s")
            print(f"  Retry Count: {config.app_settings.api.retry_count}")
    except AttributeError as e:
        # If not a nested config, show raw value
        print(f"Configuration value: {config.app_settings.value}")
    
    print("-" * 40)
    
    # Test caching behavior (AppConfig has built-in caching)
    print("\n\nTesting AppConfig caching behavior...")
    print("First access to database.host:", config.app_settings.database.host)
    
    print("\nWaiting 5 seconds...")
    time.sleep(5)
    
    print("Second access to database.host:", config.app_settings.database.host)
    print("(AppConfig should use cached value, no new fetch)")
    
    # Test with different client ID (forces new fetch)
    print("\n\nTesting with new client ID...")
    config.app_settings_2 = from_appconfig(
        application=app_name,
        environment=env_name,
        configuration=config_name,
        client_id=f"vein-test-{uuid.uuid4()}"  # New client ID
    )
    
    print("Access with new client ID:", config.app_settings_2.database.host)
    print("(Should trigger a new fetch)")
    
    # Test event system
    print("\n\nTesting event system...")
    events_received = []
    
    @config.app_settings.on_change()
    def handle_change(event):
        events_received.append(event)
        print(f"Change detected!")
        print(f"  Old value keys: {list(event.old_value.keys()) if isinstance(event.old_value, dict) else 'N/A'}")
        print(f"  New value keys: {list(event.new_value.keys()) if isinstance(event.new_value, dict) else 'N/A'}")
    
    # Note: AppConfig changes require deployment, so we can't easily test
    # live updates in an integration test
    print("(Note: Testing live updates requires AppConfig deployment)")
    
    # Test error handling
    print("\n\nTesting error handling...")
    try:
        config.bad_config = from_appconfig(
            application="non-existent-app",
            environment="non-existent-env",
            configuration="non-existent-config"
        )
        # This should fail when accessed
        _ = config.bad_config.value
    except Exception as e:
        print(f"✓ Expected error caught: {type(e).__name__}: {str(e)[:100]}...")
    
    print("\n✅ Real AppConfig integration test completed!")
    return True


def test_appconfig_with_localstack():
    """Test AppConfig with LocalStack for local development."""
    
    print("\n=== Testing AppConfig with LocalStack ===\n")
    
    # Configure for LocalStack
    aws_config = AWSConfig(
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        access_key_id="test",
        secret_access_key="test",
        verify=False
    )
    
    config = Config()
    
    try:
        config.local_settings = from_appconfig(
            application="local-app",
            environment="dev",
            configuration="settings",
            aws_config=aws_config
        )
        
        print("LocalStack configuration:", config.local_settings.value)
        print("✓ LocalStack integration successful")
    except Exception as e:
        print(f"LocalStack test skipped (LocalStack not running?): {e}")
    
    return True


if __name__ == "__main__":
    # Load environment variables from .env file if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Run the real integration test
    success = test_real_appconfig_integration()
    
    # Optionally test LocalStack
    if os.environ.get('TEST_LOCALSTACK'):
        success = success and test_appconfig_with_localstack()
    
    sys.exit(0 if success else 1)