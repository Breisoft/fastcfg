import os
from typing import Optional

from fastcfg.backoff import BackoffPolicy
from fastcfg.cache import Cache
from fastcfg.config.items import LiveConfigItem
from fastcfg.sources.files.ini import IniTracker
from fastcfg.sources.files.json import JsonTracker
from fastcfg.sources.files.yaml import YamlTracker


def from_yaml(
    file_path: os.PathLike,
    mode: str = "r",
    encoding: str = "utf-8",
    use_cache: bool = True,
    retry: bool = False,
    backoff_policy: Optional[BackoffPolicy] = None,
    cache: Optional[Cache] = None,
) -> LiveConfigItem:

    return LiveConfigItem(
        YamlTracker(
            file_path=file_path,
            mode=mode,
            encoding=encoding,
            use_cache=use_cache,
            retry=retry,
            backoff_policy=backoff_policy,
            cache=cache,
        )
    )


def from_json(
    file_path: os.PathLike,
    mode: str = "r",
    encoding: str = "utf-8",
    use_cache: bool = True,
    retry: bool = False,
    backoff_policy: Optional[BackoffPolicy] = None,
    cache: Optional[Cache] = None,
) -> LiveConfigItem:

    return LiveConfigItem(
        JsonTracker(
            file_path=file_path,
            mode=mode,
            encoding=encoding,
            use_cache=use_cache,
            retry=retry,
            backoff_policy=backoff_policy,
            cache=cache,
        )
    )


def from_ini(
    file_path: os.PathLike,
    mode: str = "r",
    encoding: str = "utf-8",
    use_cache: bool = True,
    retry: bool = False,
    backoff_policy: Optional[BackoffPolicy] = None,
    cache: Optional[Cache] = None,
) -> LiveConfigItem:

    return LiveConfigItem(
        IniTracker(
            file_path=file_path,
            mode=mode,
            encoding=encoding,
            use_cache=use_cache,
            retry=retry,
            backoff_policy=backoff_policy,
            cache=cache,
        )
    )
