from fastcfg.sources.files.file_state_tracker import IFileStateTracker
import os

from fastcfg.exceptions import MissingDependencyError, FileReadError

from typing import Optional

from fastcfg.backoff import BackoffPolicy
from fastcfg.cache import Cache

import json


class JsonTracker(IFileStateTracker):

    def __init__(self, file_path: os.PathLike,
                 mode: str = 'r', encoding: str = 'utf-8',
                 use_cache: bool = True,
                 retry: bool = False,
                 backoff_policy: Optional[BackoffPolicy] = None,
                 cache: Optional[Cache] = None, *args, **kwargs):

        super().__init__(file_path=file_path, mode=mode, encoding=encoding, use_cache=use_cache,
                         retry=retry, backoff_policy=backoff_policy, cache=cache)

        self._callable = callable

        self._file_path = file_path
        self._mode = mode
        self._encoding = encoding

        self._args = args
        self._kwargs = kwargs

    def read_file(self):
        """Reads the file at the given path."""

        try:
            with open(self._file_path, self._mode, encoding=self._encoding) as stream:
                data = json.load(stream, *self._args, **self._kwargs)

                return data
        except Exception as exc:
            raise FileReadError from exc
