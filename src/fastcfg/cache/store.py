"""
This module provides a global store for managing multiple cache instances.

Classes:
    CacheStore: A class that provides a centralized store for cache instances, allowing for adding, retrieving, and clearing caches globally.

Global Variables:
    cache_store (CacheStore): A global instance of the CacheStore class for managing cache instances.

Usage Example:
    from fastcfg.cache.store import cache_store
    from fastcfg.cache import Cache

    # Create a new cache instance
    # Automatically added to global store internally
    my_cache = Cache(name='my_cache')

    # Retrieve the cache from the global store
    retrieved_cache = cache_store.get_cache('my_cache')

    # Clear a specific cache
    cache_store.clear_cache('my_cache')

    # Clear all caches
    cache_store.clear_all_caches()
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from fastcfg.cache import Cache
else:
    Cache = None


class CacheStore:
    """
    A global store for managing multiple cache instances.

    Purpose:
        - This class provides a centralized store for cache instances.
        - It allows for adding, retrieving, and clearing caches globally.

    Attributes:
        _caches (set): A set to store cache instances.

    Methods:
        add_cache(cache): Adds a cache instance to the global store.
        clear_all_caches(): Clears all caches in the global store.
        clear_cache(cache_name): Clears a specific cache by name.
        get_cache(cache_name): Retrieves a specific cache by name.
    """

    def __init__(self):
        self._caches = {}

    def add_cache(self, cache: Cache):
        """
        Adds a cache to the global store.

        Args:
            cache_name (str): The name of the cache.
            cache (Cache): The cache instance to add.

        Raises:
            ValueError: If a cache with the same name already exists.
        """

        if cache.name in self._caches:
            raise ValueError(
                f"Cache with name {cache.name} already exists. Cache names must be globally unique."
            )

        self._caches[cache.name] = cache

    def clear_all_caches(self):
        """
        Clears all caches globally.
        """
        for cache in self._caches.values():
            cache.clear()

    def clear_cache(self, cache_name: str):
        """
        Clears a specific cache.

        Args:
            cache_name (str): The name of the cache to clear.
        """
        if cache_name in self._caches:
            self._caches[cache_name].clear()

    def get_cache(self, cache_name: str) -> Optional[Cache]:
        """
        Retrieves a specific cache if it exists.

        Args:
            cache_name (str): The name of the cache to retrieve.

        Returns:
            Optional[Cache]: The cache instance if found, otherwise None.
        """
        return self._caches.get(cache_name)


# Global instance of CacheStore
cache_store = CacheStore()
