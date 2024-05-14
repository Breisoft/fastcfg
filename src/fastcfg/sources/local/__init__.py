from fastcfg.config import Config

from typing import Callable, Optional
import os

from fastcfg.backoff import BackoffPolicy
from fastcfg.cache import Cache

from fastcfg.sources.local.environment import EnvironmentLiveTracker
from fastcfg.sources.local.callable import CallableTracker
from fastcfg.sources.local.yaml import YamlTracker
from fastcfg.config.items import LiveConfigItem


def from_os_environ(key: str) -> LiveConfigItem:
    return LiveConfigItem(EnvironmentLiveTracker(key))


def from_callable(callable: Callable, *args, **kwargs) -> LiveConfigItem:
    return LiveConfigItem(CallableTracker(callable, *args, **kwargs))


def from_yaml(file_path: os.PathLike,
              mode: str = 'r',
              encoding: str = 'utf-8',
              use_cache: bool = True,
              retry: bool = False,
              backoff_policy: Optional[BackoffPolicy] = None,
              cache: Optional[Cache] = None) -> LiveConfigItem:

    return LiveConfigItem(YamlTracker(file_path=file_path,
                                      mode=mode,
                                      encoding=encoding,
                                      use_cache=use_cache,
                                      retry=retry,
                                      backoff_policy=backoff_policy,
                                      cache=cache))
