from typing import Any
from fastcfg.config.state import ILiveTracker
from typing import Optional
from fastcfg.exceptions import MissingDependencyError

try:
    import boto3
except ImportError:
    boto3 = None


import boto3
from typing import Any, Optional
from fastcfg.config.state import ILiveTracker
from fastcfg.exceptions import MissingDependencyError


class AWSCredentialsTracker(ILiveTracker):
    """Concrete class implementing an AWS live tracker with optional custom credential rotation."""

    def __init__(self, rotate_function: Optional[callable] = None):
        self._rotate_function = rotate_function
        self._session = None

    def get_state_value(self) -> Any:
        if not boto3:
            raise MissingDependencyError('boto3')

        if self._rotate_function:
            access_key, secret_key = self._rotate_function()
            if not self._session or self._session.get_credentials().access_key != access_key:
                self._session = boto3.Session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
        elif not self._session:
            self._session = boto3.Session()

        return self._session
