from abc import abstractmethod
from typing import Any

from fastcfg.config.state import AbstractLiveStateTracker
from fastcfg.exceptions import MissingDependencyError

try:
    import boto3
except ImportError:
    boto3 = None


class IBoto3LiveTracker(AbstractLiveStateTracker):
    """Concrete class implementing an AWS live tracker with retry support."""

    def __init__(self, aws_service: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._client = boto3.client(aws_service)

    def get_state_value(self) -> Any:

        if boto3 is None:
            raise MissingDependencyError("boto3")

        return self.execute_aws()

    @abstractmethod
    def execute_aws(self):
        pass


