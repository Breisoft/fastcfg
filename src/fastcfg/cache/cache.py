from abc import ABC, abstractmethod

from typing import Any


class CacheMeta():
    pass


class ICache(ABC):

    def __init__(self):

        self._cache: dict[str, CacheMeta] = {}

    def set_value(self, key: str, value: Any):
        self._cache[key] = value

    @abstractmethod
    def is_valid(self, key: str) -> bool:
        pass

    @abstractmethod
    def on_invalidation(self, key: str) -> Any:
        pass

    def get_value(self, key: str) -> Any:
        if key in self._cache:
            if self.is_valid(key):
                return self._cache[key]
            else:
                value = self.on_invalidation(key)
                return value
        else:
            raise KeyError(f'Key `{key}` not found in cache.')
