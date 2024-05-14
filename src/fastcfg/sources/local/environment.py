from fastcfg.config.state import IStateTracker
import os

from fastcfg.exceptions import MissingEnvironmentVariableError


class EnvironmentLiveTracker(IStateTracker):

    def __init__(self, key: str):
        self._key = key

    def get_state_value(self):

        try:
            return os.environ[self._key]
        except KeyError as exc:
            raise MissingEnvironmentVariableError(self._key) from exc
