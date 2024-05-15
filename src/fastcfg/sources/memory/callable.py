from fastcfg.config.state import IStateTracker
from typing import Callable


class CallableTracker(IStateTracker):

    def __init__(self, callable: Callable, *args, **kwargs) -> None:
        self._callable = callable

        self._args = args
        self._kwargs = kwargs

    def get_state_value(self):
        return self._callable(*self._args, **self._kwargs)
