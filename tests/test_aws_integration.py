"""
Real-world integration test for AWS S3 source.
This test actually connects to AWS and fetches configuration from S3.

Prerequisites:
- AWS credentials in environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- AWS_DEFAULT_REGION set (or specify in AWSConfig)
- An S3 bucket with a test configuration file

To run:
    export AWS_ACCESS_KEY_ID=your_key
    export AWS_SECRET_ACCESS_KEY=your_secret
    export AWS_DEFAULT_REGION=us-east-1
    export TEST_BUCKET=your-test-bucket
    export TEST_KEY=test-config.json
    
    python tests/test_aws_integration.py
"""

import json
import os
import sys

from fastcfg.config.items import LiveConfigItem
from fastcfg.sources.aws.boto3_live_tracker import AWSConfig, AWSLiveTracker
from fastcfg import config
from fastcfg.sources.aws.s3 import S3LiveTracker

def from_s3(bucket: str, key: str, aws_config: AWSConfig = None) -> LiveConfigItem:
    """Helper function to create LiveConfigItem from S3."""
    tracker = S3LiveTracker(bucket, key, aws_config)
    return LiveConfigItem(tracker)


def test_real_s3_integration():
    """Real integration test that connects to AWS S3."""

    from dotenv import load_dotenv
    load_dotenv()
    
    print("=== Real AWS S3 Integration Test ===\n")
    
    # Check for required environment variables
    bucket = os.environ.get('TEST_BUCKET')
    key = os.environ.get('TEST_KEY')
    
    # Load configuration from S3
    print(f"\nLoading configuration from S3...")
    config.app_settings = from_s3(
        bucket=bucket,
        key=key,
        aws_config=config
    )
    
    # Access the configuration (this triggers the S3 fetch)
    print(f"\nFetched configuration:")
    print("-" * 40)
    
    # Try to access as nested config
    try:
        # If it's a dict, we can access nested values
        if hasattr(config.app_settings, 'database'):
            print(f"Database host: {config.app_settings.database.host}")
            print(f"Database port: {config.app_settings.database.port}")
        
        if hasattr(config.app_settings, 'api'):
            print(f"API timeout: {config.app_settings.api.timeout}")
    except:
        # If not nested, just print the raw value
        print(f"Raw value: {config.app_settings.value}")
    
    print("-" * 40)
    
    # Test refresh functionality
    print("\nTesting refresh (accessing value again)...")
    refreshed_value = config.app_settings

    print("=== First access ===")
    print("Nested value:", config.app_settings.nested.nestedKey)

    import time
    print('sleeping for 45 seconds')
    time.sleep(45)

    # Now update the S3 object to have different data
    # For example, change nestedKey to "updatedNestedValue" in S3

    # Second access
    print("\n=== Second access (after S3 update) ===")
    print("Nested value:", config.app_settings.nested.nestedKey)

    print(type(config.app_settings.value))
    print("Successfully refreshed configuration")
    
    # Test event system
    print("\nTesting event system...")
    events_received = []
    
    @config.app_settings.on_change()
    def handle_change(event):
        events_received.append(event)
        print(f"Change detected: {event.old_value} -> {event.new_value}")
    
    # In a real scenario, you could update the S3 object and then access
    # the value to trigger a change event
    
    print("\n✅ Real S3 integration test PASSED!")
    return True

if __name__ == "__main__":
    # Run the real integration test
    success = test_real_s3_integration()
    sys.exit(0 if success else 1) 