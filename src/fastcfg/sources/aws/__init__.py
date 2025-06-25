from .app_config import AppConfigLiveTracker


def from_app_config(
    application: str,
    environment: str,
    configuration: str,
    client_id: str,
    *args,
    **kwargs
):
    return AppConfigLiveTracker(
        application, environment, configuration, client_id, *args, **kwargs
    )
