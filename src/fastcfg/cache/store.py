class CacheStore():
    # TODO implement global store of caches, that way we can reset all caches.

    def __init__(self):
        self._caches = set()

    def add_cache(self, cache):
        """Add a cache to the global store."""

        self._caches.add(cache)

    def clear_all_caches(self):
        """Clears all caches globally."""
        pass

    def clear_cache(self, cache_name: str):
        """Clear a specific cache."""
        pass

    def get_cache(self, item):
        """Get a specific cache."""
        pass


cache_store = CacheStore()
