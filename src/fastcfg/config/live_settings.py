from dataclasses import dataclass
from typing import Optional

from fastcfg.cache import Cache
from fastcfg.cache.policies import CachePolicy
from fastcfg.backoff.policies import BackoffPolicy

# from fastcfg.circuit_breaker.policies import CircuitBreakerPolicy


@dataclass
class LiveSettings:
    """
    Encapsulates shared settings for LiveConfigItem trackers.

    Designed for easy use and consistent behavior across all live sources.
    """
    use_cache: bool = False
    cache_policy: Optional[CachePolicy] = None
    cache: Optional[Cache] = None

    retry: bool = False
    backoff_policy: Optional[BackoffPolicy] = None

    """
    use_circuit_breaker: bool = False
    circuit_breaker_policy: Optional[CircuitBreakerPolicy] = None
    """

    timeout_seconds: Optional[float] = None

    def build_cache(self) -> Optional[Cache]:
        if not self.use_cache:
            return None
        return self.cache or Cache(policy=self.cache_policy)

    def is_retry_enabled(self) -> bool:
        return self.retry

    def is_circuit_breaker_enabled(self) -> bool:
        return self.use_circuit_breaker