from fastcfg.exceptions import MissingCacheKeyError
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from collections import OrderedDict


class ICacheStrategy(ABC):
    @abstractmethod
    def is_valid(self, meta_value: Any) -> bool:
        """Determine if the cache entry is still valid based on the strategy."""
        pass

    @abstractmethod
    def on_insertion(self, key: str, value: Any, meta: Dict[str, Any]) -> None:
        """Execute cache strategy policy upon insertion."""
        pass

    @abstractmethod
    def on_invalidation(self, key: str, cache: 'Cache') -> Optional[Any]:
        """Perform actions upon cache invalidation, possibly providing fallback data."""
        pass

    def on_access(self, key: str, meta: Dict[str, Any]) -> None:
        """Update metadata or perform actions upon cache access."""
        pass


class Cache:
    def __init__(self, cache_strategy: ICacheStrategy):
        self._cache_strategy = cache_strategy
        self._cache: Dict[str, Any] = {}
        self._meta: Dict[str, Any] = {}

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


class IUsageCacheStrategy(ICacheStrategy):
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._order: OrderedDict[str, Any] = OrderedDict()

    def is_valid(self, meta_value: Optional[Any]) -> bool:
        """Usage-based cache entries are always valid if present."""
        return meta_value is not None

    def _remove_excess_entries(self, meta: Dict[str, Any], to_remove_key: str) -> None:
        """Remove the excess entry if capacity is exceeded."""
        if to_remove_key in self._order:
            del self._order[to_remove_key]
            del meta[to_remove_key]

    def on_invalidation(self, key: str, cache: 'Cache') -> None:
        """Perform any invalidation cleanup for a given cache key."""
        pass
