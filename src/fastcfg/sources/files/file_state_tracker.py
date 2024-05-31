from fastcfg.config.state import AbstractLiveStateTracker
import os

from typing import Optional

from fastcfg.backoff import BackoffPolicy
from fastcfg.cache import Cache

from fastcfg.exceptions import FileReadError


class AbstractFileStateTracker(AbstractLiveStateTracker):

    def __init__(self, file_path: os.PathLike,
                 mode: str = 'r', encoding: str = 'utf-8',
                 use_cache: bool = True,
                 retry: bool = False,
                 backoff_policy: Optional[BackoffPolicy] = None,
                 cache: Optional[Cache] = None):

        super().__init__(use_cache=use_cache, retry=retry,
                         backoff_policy=backoff_policy, cache=cache)

        self._callable = callable

        self._file_path = file_path
        self._mode = mode
        self._encoding = encoding

    def read_file(self):
        """Reads the file at the given path."""

        try:
            with open(self._file_path, self._mode, encoding=self._encoding) as stream:
                return stream.read()
        except Exception as exc:
            raise FileReadError from exc

    def get_state_value(self):
        return self.read_file()
