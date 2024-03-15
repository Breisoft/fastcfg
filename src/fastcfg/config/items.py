from abc import ABC, abstractmethod
from typing import Any
import os


class IConfigItem(ABC):

    @property
    @abstractmethod
    def value(self) -> Any:
        pass


class BuiltInConfigItem(IConfigItem):

    def __init__(self, value: Any):

        self._value = value

    @property
    def value(self) -> Any:
        return self._value


class LiveTracker(ABC):

    def __init__(self, key):
        self._key = key

    @abstractmethod
    def get_state(self):
        pass


class EnvironmentStateTracker(LiveTracker):

    def get_state(self):
        return os.environ[self._key]


class LiveConfigItem(IConfigItem):

    def __init__(self, state_tracker):

        super().__init__()

        self._state_tracker = state_tracker

    @property
    def value(self) -> Any:
        return self._state_tracker.get_state()
