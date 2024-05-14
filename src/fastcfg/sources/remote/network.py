from fastcfg.config.state import ILiveTracker
from fastcfg.cache import Cache
from fastcfg.exceptions import NetworkError

import requests


class RequestsLiveTracker(ILiveTracker):
    """Concrete class implementing a network tracker with retry support."""

    def __init__(self, url, method, retry: bool = False, use_cache: bool = False,
                 backoff_policy=None, cache: Cache = None, *args, **kwargs):

        super().__init__(retry, use_cache, backoff_policy, cache)

        self._url = url
        self._method = method
        self._args = args
        self._kwargs = kwargs

    def get_state_value(self):
        """Network request function implementation."""
        try:
            req_func = getattr(requests, self._method)
            return req_func(self._url, *self._args, **self._kwargs)
        except requests.exceptions.RequestException as exc:
            raise NetworkError from exc
