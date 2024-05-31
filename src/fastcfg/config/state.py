import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from fastcfg.backoff import exponential_backoff
from fastcfg.backoff.policies import BackoffPolicy
from fastcfg.cache import Cache
from fastcfg.default import defaults
from fastcfg.exceptions import MissingCacheKeyError


class AbstractStateTracker(ABC):
    """
    Abstract base class for a state tracker which is used to fetch the current state for LiveConfigItems.

    Purpose:
        - This class defines a common interface for state trackers.
        - It ensures that all state trackers can fetch the current state through a consistent method.

    Methods:
        get_state(): Fetches the state by calling `get_state_value()`.
        get_state_value(): Abstract method to fetch the internal state, must be implemented by subclasses.
    """

    def get_state(self) -> Any:
        """
        Fetches the state.

        Calls `get_state_value()` and returns the result by default.
        Child classes may override this behavior.

        Returns:
            Any: The current state.
        """
        return self.get_state_value()

    @abstractmethod
    def get_state_value(self) -> Any:
        """
        Fetches the internal state.

        Must be implemented by child classes to define the actual state fetching logic.

        Returns:
            Any: The internal state.
        """
        pass


class RetriableMixin:
    """
    Mixin providing retry logic.

    Purpose:
        - This mixin adds retry capabilities to state tracker classes that need to handle transient failures.
        - It uses an exponential backoff strategy to retry operations.

    Attributes:
        _retry (bool): Whether to enable retry logic.
        _backoff_policy (BackoffPolicy): The backoff policy to use.

    Methods:
        _call_retriable_function(func, *args, **kwargs): Calls a function with optional backoff.
    """

    def __init__(self, retry: bool = False, backoff_policy: BackoffPolicy = None):
        """
        Initializes the RetriableMixin.

        Args:
            retry (bool): Whether to enable retry logic.
            backoff_policy (BackoffPolicy, optional): The backoff policy to use. Defaults to `defaults.backoff_policy`.
            See `fastcfg.default` package for more details.
        """
        self._retry = retry
        self._backoff_policy = backoff_policy or defaults.backoff_policy

    def _call_retriable_function(
        self, func: Callable[..., Any], *args, **kwargs
    ) -> Any:
        """
        Calls a function with optional backoff.

        Args:
            func (Callable[..., Any]): The function to call.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the function call.
        """
        if self._retry:
            wrapped = exponential_backoff(self._backoff_policy)(func)
            return wrapped(*args, **kwargs)
        else:
            return func(*args, **kwargs)


class CacheMixin:
    """Mixin providing caching logic."""

    def __init__(self, use_cache: bool = False, cache: Optional[Cache] = None):
        """
        Initializes the CacheMixin.

        Args:
            use_cache (bool): Whether to enable caching.
            cache (Cache, optional): The cache instance to use. Defaults to `None`.
                If `None` and `use_cache` is True, a new cache instance is created with the default cache policy.
        """
        if cache is None and use_cache:
            self._cache = Cache(defaults.cache_policy)
        else:
            self._cache = cache

    def _call_cached_function(
        self, key: str, func: Callable[..., Any], *args, **kwargs
    ) -> Any:
        """
        Calls a function with optional caching.

        Args:
            key (str): The cache key.
            func (Callable[..., Any]): The function to call.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the function call.
        """
        if self._cache:
            try:
                return self._cache.get_value(key)
            except MissingCacheKeyError:
                value = func(*args, **kwargs)
                self._cache.set_value(key, value)
                return value
        else:
            return func(*args, **kwargs)


class AbstractLiveStateTracker(AbstractStateTracker, RetriableMixin, CacheMixin, ABC):
    """
    Base class for state trackers with optional retry and caching.
    This class provides the basis for all StateTrackers that are
    dynamically fetched on attribute access from a `Config` instance.

    Purpose:
        - This class combines state tracking, retry logic, and caching capabilities.
        - It provides a unified interface for fetching state with support for retries and caching.

    Attributes:
        _cache_uuid_key (str): The cache key for the state.

    Methods:
        __init__(retry, use_cache, backoff_policy, cache): Initializes the ILiveTracker.
        get_state(): Fetches the state with retry and caching support.
    """

    def __init__(
        self,
        retry: bool = False,
        use_cache: bool = False,
        backoff_policy: Optional[BackoffPolicy] = None,
        cache: Optional[Cache] = None,
    ):
        """
        Initializes the ILiveTracker.

        Args:
            retry (bool): Whether to enable retry logic.
            use_cache (bool): Whether to enable caching.
            backoff_policy (BackoffPolicy, optional): The backoff policy to use. Defaults to `None`.
            cache (Cache, optional): The cache instance to use. Defaults to `None` and
            if `use_cache` is True, a new cache instance is created with the default cache policy.
        """
        if use_cache:
            # Generate cache key
            self._cache_uuid_key = str(uuid.uuid4())
        else:
            self._cache_uuid_key = None

        AbstractStateTracker.__init__(self)
        RetriableMixin.__init__(self, retry, backoff_policy)
        CacheMixin.__init__(self, use_cache, cache)

    def get_state(self) -> Any:
        """
        Fetches the state with retry and caching support.

        Returns:
            Any: The current state.
        """
        return self._call_cached_function(
            self._cache_uuid_key, self._call_retriable_function, self.get_state_value
        )
