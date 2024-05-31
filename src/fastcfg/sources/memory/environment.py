import os

from fastcfg.config.state import AbstractStateTracker
from fastcfg.exceptions import MissingEnvironmentVariableError


class EnvironmentLiveTracker(AbstractStateTracker):

    def __init__(self, key: str):
        self._key = key

    def get_state_value(self):

        try:
            return os.environ[self._key]
        except KeyError as exc:
            raise MissingEnvironmentVariableError(self._key) from exc
