from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from collections import OrderedDict
import uuid

from fastcfg.exceptions import MissingCacheKeyError
from fastcfg.cache.store import cache_store


class AbstractCacheStrategy(ABC):
    """
    An abstract base class that defines the interface for cache strategies.

    Methods:
        - is_valid(meta_value: Any) -> bool: Determine if a cache entry is still valid.
        - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Execute policy upon cache insertion.
        - on_invalidation(key: str, cache: 'Cache') -> Optional[Any]: Perform actions upon cache invalidation.
        - on_access(key: str, meta: Dict[str, Any]) -> None: Update metadata or perform actions upon cache access.
    """

    @abstractmethod
    def is_valid(self, meta_value: Any) -> bool:
        """Determine if the cache entry is still valid based on the strategy."""
        pass

    @abstractmethod
    def on_insertion(self, key: str, value: Any, meta: Dict[str, Any]) -> None:
        """Execute cache strategy policy upon insertion."""
        pass

    def on_invalidation(self, key: str, cache: 'Cache') -> Optional[Any]:
        """Perform actions upon cache invalidation, implement this on child classes if you need this functionality."""
        pass

    def on_access(self, key: str, meta: Dict[str, Any]) -> None:
        """Update metadata or perform actions upon cache access."""
        pass


class AbstractUsageCacheStrategy(AbstractCacheStrategy, ABC):
    """
    An abstract base class of ICacheStrategy that implements usage-based cache eviction.

    Methods:
        - __init__(capacity: int): Initialize the strategy with a given capacity.
        - is_valid(meta_value: Optional[Any]) -> bool: Determine if a cache entry is valid based on usage.
        - _remove_excess_entries(meta: Dict[str, Any], to_remove_key: str) -> None: Remove excess entries if capacity is exceeded.
        - on_invalidation(key: str, cache: 'Cache') -> None: Perform any invalidation cleanup for a given cache key.
        - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Execute cache strategy policy upon insertion.
        - on_access(key: str, meta: Dict[str, Any]) -> None: Update metadata or perform actions upon cache access.
    """

    def __init__(self, capacity: int):
        """
        Initialize the strategy with a given capacity.

        Args:
            capacity (int): The maximum number of entries the cache can hold.
        """
        self._capacity = capacity
        self._order: OrderedDict[str, Any] = OrderedDict()

    def is_valid(self, meta_value: Optional[Any]) -> bool:
        """
        Determine if a cache entry is valid based on usage.

        Args:
            meta_value (Optional[Any]): The metadata value to check.

        Returns:
            bool: True if the entry is valid, False otherwise.
        """
        return meta_value is not None

    def _remove_excess_entries(self, meta: Dict[str, Any], to_remove_key: str) -> None:
        """
         Remove the excess entry if capacity is exceeded.

         Args:
             meta (Dict[str, Any]): The metadata dictionary.
             to_remove_key (str): The key of the entry to remove.
         """
        if to_remove_key in self._order:
            del self._order[to_remove_key]
            del meta[to_remove_key]

    def on_invalidation(self, key: str, cache: 'Cache') -> None:
        """
        Perform any invalidation cleanup for a given cache key.

        Args:
            key (str): The key of the entry to invalidate.
            cache (Cache): The cache instance.
        """
        pass

    @abstractmethod
    def on_insertion(self, key: str, value: Any, meta: Dict[str, Any]) -> None:
        """Execute cache strategy policy upon insertion."""
        pass

    @abstractmethod
    def on_access(self, key: str, meta: Dict[str, Any]) -> None:
        """Update metadata or perform actions upon cache access."""
        pass


class Cache:
    """
    A class that manages cache entries using a specified cache strategy.

    Methods:
        - __init__(cache_strategy: ICacheStrategy): Initialize the cache with a given strategy.
        - set_value(key: str, value: Any) -> None: Set the value and associated metadata for a given key.
        - get_value(key: str) -> Any: Retrieve the value for a given key if it's valid.
        - is_valid(key: str) -> bool: Check if a key is present and valid in the cache.
        - get_metadata(key: str) -> Optional[Any]: Get metadata associated with a given cache key.
    """

    def __init__(self, cache_strategy: AbstractCacheStrategy, name: str = None):
        self._cache_strategy = cache_strategy
        self._cache: Dict[str, Any] = {}
        self._meta: Dict[str, Any] = {}
        self._name = name

        self._handle_new_cache()

    def _handle_new_cache(self):
        """
        Handle the initialization of a new cache instance.

        Purpose:
            - This method ensures that each cache instance has a unique name.
            - If a name is not provided during initialization, it generates a unique name using UUID.
            - It then adds the cache instance to the global cache store.

        As a part of the initialization, this method also adds the cache instance to the global cache store, to keep track of all cache instances.

        Raises:
            ValueError: If a cache with the same name already exists in the global cache store.
        """

        if not self._name:
            # Generate a unique name if not provided
            self._name = str(uuid.uuid4())

        cache_store.add_cache(self._name, self)

    def set_value(self, key: str, value: Any) -> None:
        """Set the value and associated metadata for a given key in the cache."""
        self._cache[key] = value
        self._cache_strategy.on_insertion(key, value, self._meta)

    def get_value(self, key: str) -> Any:
        """Retrieve the value for a given key from the cache if it's valid."""
        if key in self._cache:
            meta_value = self._meta[key]
            if self._cache_strategy.is_valid(meta_value):
                self._cache_strategy.on_access(key, self._meta)
                return self._cache[key]
            else:
                value = self._cache_strategy.on_invalidation(key, self)
                del self._cache[key]
                del self._meta[key]
                return value
        else:
            raise MissingCacheKeyError(key)

    def is_valid(self, key: str) -> bool:
        """Check if a key is present and valid in the cache."""
        return key in self._cache and self._cache_strategy.is_valid(self._meta[key])

    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata associated with a given cache key."""
        return self._meta.get(key, None)
