from typing import Callable

from fastcfg.config.items import LiveConfigItem
from fastcfg.sources.memory.callable import CallableTracker
from fastcfg.sources.memory.environment import EnvironmentLiveTracker


def from_os_environ(key: str) -> LiveConfigItem:
    return LiveConfigItem(EnvironmentLiveTracker(key))


def from_callable(callable: Callable, *args, **kwargs) -> LiveConfigItem:
    return LiveConfigItem(CallableTracker(callable, *args, **kwargs))
