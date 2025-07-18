from typing import Optional
import json

from fastcfg.sources.aws.boto3_live_tracker import AWSConfig, AWSLiveTracker

# Try to import yaml, but make it optional
try:
    import yaml
    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False

# Example implementation of S3LiveTracker
class S3LiveTracker(AWSLiveTracker):
    """Live tracker for S3 objects."""
    
    def __init__(self, bucket: str, key: str, aws_config: Optional[AWSConfig] = None):
        super().__init__('s3', aws_config)
        self.bucket = bucket
        self.key = key
    
    def fetch_from_aws(self):
        """Fetch object from S3 and parse based on file type."""
        print(f"Fetching s3://{self.bucket}/{self.key}")
        response = self.client.get_object(Bucket=self.bucket, Key=self.key)
        content = response['Body'].read()
        
        # Get content type from S3 metadata
        content_type = response.get('ContentType', '')
        
        # Parse based on file extension or content type
        if self.key.endswith('.json') or 'json' in content_type:
            return json.loads(content)
        elif self.key.endswith('.yaml') or self.key.endswith('.yml') or 'yaml' in content_type:
            if HAS_YAML:
                return yaml.safe_load(content)
            else:
                # Return as string if yaml is not available
                print("Warning: PyYAML not installed. Install with: pip install pyyaml")
                return content.decode('utf-8')
        else:
            # Return as string for other types
            return content.decode('utf-8')