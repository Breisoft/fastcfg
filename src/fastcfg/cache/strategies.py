from fastcfg.cache import ICacheStrategy, IUsageCacheStrategy, Cache
from typing import Any, Dict, Optional
import time


class TTLCacheStrategy(ICacheStrategy):
    def __init__(self, seconds: int):
        self._seconds = seconds

    def is_valid(self, meta_value: Optional[float]) -> bool:
        """Check if the cache entry is still valid based on the time-to-live (TTL)."""

        return meta_value is not None and time.time() < meta_value

    def on_insertion(self, key: str, value: Any, meta: Dict[str, Any]) -> None:
        meta[key] = time.time() + self._seconds

    def on_invalidation(self, key: str, cache: Cache) -> None:
        """Perform any invalidation cleanup for a given cache key."""
        pass


class LRUCacheStrategy(IUsageCacheStrategy):
    def on_access(self, key: str, meta: Dict[str, Any]) -> None:
        """Update the access order to mark the key as most recently used."""
        if key in self._order:
            self._order.move_to_end(key)

        if key not in meta:
            self._order[key] = None
            if len(self._order) > self._capacity:
                lru_key = next(iter(self._order))
                self._remove_excess_entries(meta, lru_key)


class MRUCacheStrategy(IUsageCacheStrategy):
    def on_access(self, key: str, meta: Dict[str, Any]) -> None:
        """Update the access order to mark the key as most recently used."""
        if key in self._order:
            self._order.move_to_end(key, last=False)

        if key not in meta:
            self._order[key] = None
            if len(self._order) > self._capacity:
                mru_key = next(reversed(self._order))
                self._remove_excess_entries(meta, mru_key)
