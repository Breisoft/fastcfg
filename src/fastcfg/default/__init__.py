"""
This module sets up the default config for the `fastcfg` package.

Modules Imported:
    - `Config` from `fastcfg`: The main configuration class used to manage settings.
    - `TEN_MIN_TTL` from `fastcfg.cache.policies`: A caching policy with a time-to-live of ten minutes.
    - `BASIC_BACKOFF_POLICY` from `fastcfg.backoff.policies`: A basic backoff policy for retry mechanisms.

Attributes:
    defaults (Config): An instance of the `Config` class initialized with default settings for cache and backoff policies.

Usage:
    The `defaults` configuration can be used throughout the application to access and manage default settings. 
    Internally, this configuration is used to set the default cache policy and backoff policy, ensuring consistent behavior across the codebase.

    Example:
        The `defaults` configuration can be used throughout the application to access and manage default settings.

    ```python
    from fastcfg.default import defaults
    # Accessing cache policy
    print(defaults.cache_policy)
    # Accessing backoff policy
    print(defaults.backoff_policy)
    ```

    We love our library so much, we use it ourselves! This default configuration shows how fastcfg maintains consistent settings internally. So meta, wow!

"""

from fastcfg import Config
from fastcfg.backoff.policies import BASIC_BACKOFF_POLICY
from fastcfg.cache.policies import TEN_MIN_TTL

defaults = Config(
    cache_policy=TEN_MIN_TTL, backoff_policy=BASIC_BACKOFF_POLICY
)
