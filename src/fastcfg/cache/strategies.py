"""
This module defines various cache strategies for use with the caching mechanism.

Classes:
    TTLCacheStrategy (ICacheStrategy): A cache strategy that invalidates entries based on a time-to-live (TTL) value.
        - Attributes:
            - _seconds (int): The TTL value in seconds.
        - Methods:
            - __init__(seconds: int): Initialize the strategy with a TTL value.
            - is_valid(meta_value: Optional[float]) -> bool: Check if the cache entry is still valid based on the TTL.
            - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Set the TTL for a cache entry upon insertion.
            - on_invalidation(key: str, cache: Cache) -> None: Perform any invalidation cleanup for a given cache key.

    LRUCacheStrategy (IUsageCacheStrategy): A cache strategy that evicts the least recently used (LRU) entries when capacity is exceeded.
        - Methods:
            - on_access(key: str, meta: Dict[str, Any]) -> None: Update the access order to mark the key as most recently used.
            - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Handle insertion and evict if necessary.

    MRUCacheStrategy (IUsageCacheStrategy): A cache strategy that evicts the most recently used (MRU) entries when capacity is exceeded.
        - Methods:
            - on_access(key: str, meta: Dict[str, Any]) -> None: Update the access order to mark the key as most recently used.
            - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Handle insertion and evict if necessary.
"""

from typing import Any, Dict, Optional
import time


from fastcfg.cache import AbstractCacheStrategy, AbstractUsageCacheStrategy, Cache


class TTLCacheStrategy(AbstractCacheStrategy):
    """
    A cache strategy that invalidates entries based on a time-to-live (TTL) value.

    Attributes:
        _seconds (int): The TTL value in seconds.

    Methods:
        - __init__(seconds: int): Initialize the strategy with a TTL value.
        - is_valid(meta_value: Optional[float]) -> bool: Check if the cache entry is still valid based on the TTL.
        - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Set the TTL for a cache entry upon insertion.
        - on_invalidation(key: str, cache: Cache) -> None: Perform any invalidation cleanup for a given cache key.
    """

    def __init__(self, seconds: int):
        """
        Initialize the strategy with a TTL value.

        Args:
            seconds (int): The TTL value in seconds.
        """
        self._seconds = seconds

    def is_valid(self, meta_value: Optional[float]) -> bool:
        """
        Check if the cache entry is still valid based on the TTL.

        Args:
            meta_value (Optional[float]): The metadata value to check.

        Returns:
            bool: True if the entry is still valid, False otherwise.
        """
        return meta_value is not None and time.time() < meta_value

    def on_insertion(self, key: str, value: Any, meta: Dict[str, Any]) -> None:
        """
        Set the TTL for a cache entry upon insertion.

        Args:
            key (str): The cache key.
            value (Any): The cache value.
            meta (Dict[str, Any]): The metadata dictionary.
        """
        meta[key] = time.time() + self._seconds

    def on_invalidation(self, key: str, cache: Cache) -> None:
        """
        Perform any invalidation cleanup for a given cache key.

        Args:
            key (str): The cache key.
            cache (Cache): The cache instance.
        """
        pass


class LRUCacheStrategy(AbstractUsageCacheStrategy):
    """
    A cache strategy that evicts the least recently used (LRU) entries when capacity is exceeded.

    Methods:
        - on_access(key: str, meta: Dict[str, Any]) -> None: Update the access order to mark the key as most recently used.
        - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Handle insertion and evict if necessary.
    """

    def __init__(self, capacity: int):
        """
        Initialize the strategy with a capacity value.

        Args:
            capacity (int): The maximum number of entries that can be stored in the cache.
        """
        super().__init__(capacity=capacity)

    def on_access(self, key: str, meta: Dict[str, Any]) -> None:
        """
        Update the access order to mark the key as most recently used.

        Args:
            key (str): The cache key.
            meta (Dict[str, Any]): The metadata dictionary.
        """
        if key in self._order:
            self._order.move_to_end(key)

    def on_insertion(self, key: str, value: Any, meta: Dict[str, Any]) -> None:
        """
        Handle insertion and evict if necessary.

        Args:
            key (str): The cache key.
            value (Any): The cache value.
            meta (Dict[str, Any]): The metadata dictionary.
        """
        self._order[key] = None
        if len(self._order) > self._capacity:
            lru_key = next(iter(self._order))
            self._remove_excess_entries(meta, lru_key)


class MRUCacheStrategy(AbstractUsageCacheStrategy):
    """
    A cache strategy that evicts the most recently used (MRU) entries when capacity is exceeded.

    Methods:
        - on_access(key: str, meta: Dict[str, Any]) -> None: Update the access order to mark the key as most recently used.
        - on_insertion(key: str, value: Any, meta: Dict[str, Any]) -> None: Handle insertion and evict if necessary.
    """

    def __init__(self, capacity: int):
        """
        Initialize the strategy with a capacity value.

        Args:
            capacity (int): The maximum number of entries that can be stored in the cache.
        """
        super().__init__(capacity=capacity)

    def on_access(self, key: str, meta: Dict[str, Any]) -> None:
        """
        Update the access order to mark the key as most recently used.

        Args:
            key (str): The cache key.
            meta (Dict[str, Any]): The metadata dictionary.
        """
        if key in self._order:
            self._order.move_to_end(key, last=False)

    def on_insertion(self, key: str, value: Any, meta: Dict[str, Any]) -> None:
        """
        Handle insertion and evict if necessary.

        Args:
            key (str): The cache key.
            value (Any): The cache value.
            meta (Dict[str, Any]): The metadata dictionary.
        """
        self._order[key] = None
        if len(self._order) > self._capacity:
            mru_key = next(reversed(self._order))
            self._remove_excess_entries(meta, mru_key)
