from abc import abstractmethod, ABC

from fastcfg.cache import Cache
from fastcfg.default import defaults
from fastcfg.backoff import exponential_backoff
from fastcfg.backoff.policies import BackoffPolicy
from fastcfg.exceptions import MissingCacheKeyError

import uuid
from typing import Any, Callable, Optional


class IStateTracker(ABC):
    """Abstract base class representing a state tracker."""

    def get_state(self) -> Any:
        """Fetch the state. Calls get_state_value() and returns the result by default. Child classes may change this behavior."""
        return self.get_state_value()

    @abstractmethod
    def get_state_value(self) -> Any:
        """Fetch the internal state. Child classes must implement this. It's used to implement the actual state fetching logic."""
        pass


class RetriableMixin:
    """Mixin providing retry logic."""

    def __init__(self, retry: bool = False, backoff_policy: BackoffPolicy = None):
        self._retry = retry
        self._backoff_policy = backoff_policy or defaults.backoff_policy

    def _call_retriable_function(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Wrapper to call a function with optional backoff."""
        if self._retry:
            wrapped = exponential_backoff(self._backoff_policy)(func)
            return wrapped(*args, **kwargs)
        else:
            return func(*args, **kwargs)


class CacheMixin:
    """Mixin providing caching logic."""

    def __init__(self, use_cache: bool = False, cache: Optional[Cache] = None):
        if cache is None and use_cache:
            self._cache = Cache(defaults.cache_policy)
        else:
            self._cache = cache

    def _call_cached_function(self, key: str, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Wrapper to call a function with optional caching."""
        if self._cache:
            try:
                return self._cache.get_value(key)
            except MissingCacheKeyError:
                value = func(*args, **kwargs)
                self._cache.set_value(key, value)
                return value
        else:
            return func(*args, **kwargs)


class ILiveTracker(IStateTracker, RetriableMixin, CacheMixin):
    """Base class for live trackers with optional retry and caching."""

    def __init__(self, retry: bool = False, use_cache: bool = False,
                 backoff_policy: Optional[BackoffPolicy] = None, cache: Optional[Cache] = None):

        if use_cache:
            self._cache_uuid_key = str(uuid.uuid4())
        else:
            self._cache_uuid_key = None

        IStateTracker.__init__(self)
        RetriableMixin.__init__(self, retry, backoff_policy)
        CacheMixin.__init__(self, use_cache, cache)

    def get_state(self) -> Any:
        """Fetch the state with retry and caching support."""
        return self._call_cached_function(self._cache_uuid_key, self._call_retriable_function, self.get_state_value)
