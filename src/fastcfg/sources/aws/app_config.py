import json

from fastcfg.sources.aws.boto3_live_tracker import IBoto3LiveTracker


class AppConfigLiveTracker(IBoto3LiveTracker):
    """Concrete class implementing AWS AppConfig interaction."""

    def __init__(
        self,
        application: str,
        environment: str,
        configuration: str,
        client_id: str,
        *args,
        **kwargs
    ):
        super().__init__("appconfig")
        self._application = application
        self._environment = environment
        self._configuration = configuration
        self._client_id = client_id

        self._args = args
        self._kwargs = kwargs

    def execute_aws(self):

        print("executing aws!")

        response = self._client.get_configuration(
            Application=self._application,
            Environment=self._environment,
            Configuration=self._configuration,
            ClientId=self._client_id,
            *self._args,
            **self._kwargs
        )

        return response["Content"].read().decode("utf-8")
