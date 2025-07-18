import configparser
import os
from typing import Optional

from fastcfg.backoff import BackoffPolicy
from fastcfg.cache import Cache
from fastcfg.exceptions import FileReadError
from fastcfg.sources.files.file_loader import AbstractFileStateTracker


class IniTracker(AbstractFileStateTracker):

    def __init__(
        self,
        file_path: os.PathLike,
        mode: str = "r",
        encoding: str = "utf-8",
        use_cache: bool = True,
        retry: bool = False,
        backoff_policy: Optional[BackoffPolicy] = None,
        cache: Optional[Cache] = None,
        *args,
        **kwargs
    ):

        super().__init__(
            file_path=file_path,
            mode=mode,
            encoding=encoding,
            use_cache=use_cache,
            retry=retry,
            backoff_policy=backoff_policy,
            cache=cache,
        )

        self._callable = callable

        self._file_path = file_path
        self._mode = mode
        self._encoding = encoding

        self._args = args
        self._kwargs = kwargs

    def read_file(self):
        """Reads the file at the given path."""

        try:
            config = configparser.ConfigParser()
            config.read(self._file_path, encoding=self._encoding)
            data = config._sections

            return data
        except Exception as exc:
            raise FileReadError from exc
