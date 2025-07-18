"""
Configuration options and policies for fastcfg.

This module provides a centralized location for all configuration options
and policies used throughout fastcfg, making them easily discoverable and importable.

Example:
    from fastcfg.options import AWSOptions, LiveOptions, TTLCachePolicy
    
    # Configure AWS with specific credentials
    aws_options = AWSOptions(
        region_name="us-east-1",
        profile_name="production"
    )
    
    # Configure live tracking behavior  
    live_options = LiveOptions(
        use_cache=True,
        cache_policy=TTLCachePolicy(seconds=300),
        retry=True,
        timeout_seconds=30
    )
"""

from typing import TYPE_CHECKING

# Import and rename to standardized Options naming
from fastcfg.sources.aws.boto3_live_tracker import AWSConfig as AWSOptions
from fastcfg.config.live_settings import LiveSettings as LiveOptions

# Cache strategies (using Policy suffix for consistency)
from fastcfg.cache.strategies import (
    TTLCacheStrategy as TTLCachePolicy,
    LRUCacheStrategy as LRUCachePolicy,
    MRUCacheStrategy as MRUCachePolicy,
)

# Pre-configured cache policies
from fastcfg.cache.policies import (
    TEN_MIN_TTL as TenMinuteTTLPolicy,
    ONE_HOUR_TTL as OneHourTTLPolicy, 
    DAILY_TTL as DailyTTLPolicy,
    LRU_POLICY as DefaultLRUPolicy,
    MRU_POLICY as DefaultMRUPolicy,
)

# Backoff policies
from fastcfg.backoff import BackoffPolicy
from fastcfg.backoff.policies import BASIC_BACKOFF_POLICY as BasicBackoffPolicy

# Validation policies
from fastcfg.validation.policies import (
    TypeValidator as TypeValidationPolicy,
    RangeValidator as RangeValidationPolicy,
    RegexValidator as RegexValidationPolicy,
    PydanticValidator as PydanticValidationPolicy,
)

# Create aliases for backward compatibility
if TYPE_CHECKING:
    # Type hints use the actual classes
    pass
else:
    # Runtime can use the original names too
    AWSConfig = AWSOptions
    LiveSettings = LiveOptions

# Export all
__all__ = [
    # Configuration Options
    'AWSOptions',
    'LiveOptions',

     # Validation Policies
    'TypeValidationPolicy',
    'RangeValidationPolicy', 
    'RegexValidationPolicy',
    'PydanticValidationPolicy',
    
    # Cache Policies
    'TTLCachePolicy', 
    'LRUCachePolicy',
    'MRUCachePolicy',
    
    # Pre-configured Cache Policies
    'TenMinuteTTLPolicy',
    'OneHourTTLPolicy',
    'DailyTTLPolicy',
    'DefaultLRUPolicy',
    'DefaultMRUPolicy',
    
    # Backoff Policies
    'BackoffPolicy',
    'BasicBackoffPolicy',
]