from fastcfg.config.items import LiveConfigItem
from fastcfg.sources.remote.network import RequestsLiveTracker


def from_requests(url: str, method: str, retry: bool = False, *args, **kwargs):

    return LiveConfigItem(
        RequestsLiveTracker(url, method, retry, *args, **kwargs)
    )
