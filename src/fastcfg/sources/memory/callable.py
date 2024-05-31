from typing import Callable

from fastcfg.config.state import AbstractStateTracker


class CallableTracker(AbstractStateTracker):

    def __init__(self, callable: Callable, *args, **kwargs) -> None:
        self._callable = callable

        self._args = args
        self._kwargs = kwargs

    def get_state_value(self):
        return self._callable(*self._args, **self._kwargs)
