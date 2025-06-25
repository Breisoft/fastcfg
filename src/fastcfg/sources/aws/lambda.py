import json

from fastcfg.sources.aws import IBoto3LiveTracker


class LambdaLiveTracker(IBoto3LiveTracker):
    """Concrete class implementing a live lambda tracker."""

    def __init__(
        self,
        function_name: str,
        payload: dict,
        invocation_type: str = "RequestResponse",
        *args,
        **kwargs
    ):
        super().__init__("lambda", *args, **kwargs)
        self._function_name = function_name
        self._payload = payload
        self._invocation_type = invocation_type

        self._args = args
        self._kwargs = kwargs

    def execute_aws(self):
        response = self._client.invoke(
            FunctionName=self._function_name,
            InvocationType=self._invocation_type,
            Payload=json.dumps(self._payload),
            *self._args,
            **self._kwargs
        )

        return json.loads(response["Payload"].read())
