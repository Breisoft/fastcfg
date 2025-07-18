import json
from typing import Optional

from fastcfg.sources.aws.boto3_live_tracker import AWSLiveTracker, AWSConfig

# Try to import yaml, but make it optional
try:
    import yaml
    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False


class AppConfigLiveTracker(AWSLiveTracker):
    """Concrete class implementing AWS AppConfig interaction."""

    def __init__(
        self,
        application: str,
        environment: str,
        configuration: str,
        client_id: str,
        aws_config: Optional[AWSConfig] = None,
        *args,
        **kwargs
    ):
        super().__init__("appconfig", aws_config, *args, **kwargs)
        self._application = application
        self._environment = environment
        self._configuration = configuration
        self._client_id = client_id

    def fetch_from_aws(self):
        """Fetch configuration from AWS AppConfig."""
        response = self.client.get_configuration(
            Application=self._application,
            Environment=self._environment,
            Configuration=self._configuration,
            ClientId=self._client_id
        )

        content = response["Content"].read().decode("utf-8")
        content_type = response.get("ContentType", "")

        # Parse based on content type
        if 'json' in content_type:
            return json.loads(content)
        elif 'yaml' in content_type or 'yml' in content_type:
            if HAS_YAML:
                return yaml.safe_load(content)
            else:
                raise ValueError("PyYAML not installed. Install with: pip install pyyaml")
        else:
            # Try to auto-detect format
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try YAML if available
                if HAS_YAML:
                    try:
                        return yaml.safe_load(content)
                    except yaml.YAMLError:
                        raise ValueError("Invalid YAML format")
                # Return as plain string
                return content
