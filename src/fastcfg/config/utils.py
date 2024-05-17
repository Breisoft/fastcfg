def create_config_dict(item: dict):
    from fastcfg.config import Config
    return Config(**item)
