from abc import abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field

from fastcfg.config.state import AbstractLiveStateTracker
from fastcfg.exceptions import MissingDependencyError

try:
    import boto3
    from botocore.config import Config as BotoConfig
except ImportError:
    boto3 = None
    BotoConfig = None


@dataclass
class AWSConfig:
    """Configuration for AWS service clients.
    
    Attributes:
        region_name: AWS region (e.g., 'us-east-1'). If None, uses default from environment/config.
        access_key_id: AWS access key ID. If None, uses default from environment/config.
        secret_access_key: AWS secret access key. If None, uses default from environment/config.
        session_token: AWS session token for temporary credentials. Optional.
        profile_name: AWS profile name from ~/.aws/config. Takes precedence over explicit credentials.
        endpoint_url: Custom endpoint URL (useful for LocalStack or other AWS-compatible services).
        verify: Whether to verify SSL certificates. Can be boolean or path to CA bundle.
        max_retries: Maximum number of retry attempts.
        timeout: Request timeout in seconds.
        extra_config: Additional botocore Config options.
    """
    region_name: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    profile_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    verify: Optional[bool | str] = None
    max_retries: Optional[int] = None
    timeout: Optional[int] = None
    extra_config: dict = field(default_factory=dict)
    
    def get_boto_config(self) -> Optional['BotoConfig']:
        """Convert to botocore Config object."""
        if BotoConfig is None:
            return None
            
        config_dict = {}
        if self.max_retries is not None:
            config_dict['retries'] = {'max_attempts': self.max_retries}
        if self.timeout is not None:
            config_dict['connect_timeout'] = self.timeout
            config_dict['read_timeout'] = self.timeout
            
        # Merge with any extra config
        config_dict.update(self.extra_config)
        
        return BotoConfig(**config_dict) if config_dict else None
    
    def get_session_kwargs(self) -> dict:
        """Get kwargs for boto3.Session creation."""
        kwargs = {}
        if self.region_name:
            kwargs['region_name'] = self.region_name
        if self.profile_name:
            kwargs['profile_name'] = self.profile_name
        elif self.access_key_id and self.secret_access_key:
            kwargs['aws_access_key_id'] = self.access_key_id
            kwargs['aws_secret_access_key'] = self.secret_access_key
            if self.session_token:
                kwargs['aws_session_token'] = self.session_token
        return kwargs
    
    def get_client_kwargs(self) -> dict:
        """Get kwargs for client creation."""
        kwargs = {}
        if self.endpoint_url:
            kwargs['endpoint_url'] = self.endpoint_url
        if self.verify is not None:
            kwargs['verify'] = self.verify
        
        boto_config = self.get_boto_config()
        if boto_config:
            kwargs['config'] = boto_config
            
        return kwargs


class AWSLiveTracker(AbstractLiveStateTracker):
    """Base class for AWS service live trackers with proper credential and retry support.
    
    This class handles:
    - Credential management (explicit, profile, or environment)
    - Region configuration
    - Retry logic with exponential backoff
    - Session and client lifecycle
    - Error handling for missing dependencies
    """

    def __init__(
        self, 
        service_name: str,
        aws_config: Optional[AWSConfig] = None,
        *args, 
        **kwargs
    ):
        """Initialize AWS tracker.
        
        Args:
            service_name: AWS service name (e.g., 'appconfig', 's3', 'dynamodb')
            aws_config: AWS configuration. If None, uses default AWS credential chain.
            *args, **kwargs: Additional arguments passed to parent class
        """
        super().__init__(*args, **kwargs)
        
        if boto3 is None:
            raise MissingDependencyError(
                "boto3 is required for AWS sources. Install with: pip install vein[aws]"
            )
        
        self._service_name = service_name
        self._aws_config = aws_config or AWSConfig()
        self._session = None
        self._client = None
    
    @property
    def session(self) -> 'boto3.Session':
        """Get or create boto3 session."""
        if self._session is None:
            session_kwargs = self._aws_config.get_session_kwargs()
            self._session = boto3.Session(**session_kwargs)
        return self._session
    
    @property
    def client(self):
        """Get or create service client."""
        if self._client is None:
            client_kwargs = self._aws_config.get_client_kwargs()
            self._client = self.session.client(self._service_name, **client_kwargs)
        return self._client

    def get_state_value(self) -> Any:
        """Get state from AWS service with proper error handling."""
        try:
            return self.fetch_from_aws()
        except Exception as e:
            # Let the retry mechanism in parent class handle retries
            # Just re-raise the exception with proper context
            raise Exception(f"Failed to fetch from AWS {self._service_name}: {str(e)}") from e

    @abstractmethod
    def fetch_from_aws(self) -> Any:
        """Fetch the actual value from AWS service.
        
        Subclasses must implement this to perform the actual AWS API call.
        The client is available as self.client.
        
        Returns:
            The fetched value from AWS
            
        Raises:
            Any AWS-specific exceptions (will be handled by retry logic)
        """
        pass
