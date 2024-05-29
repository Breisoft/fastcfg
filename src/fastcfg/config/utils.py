def create_config_dict(item: dict):
    from fastcfg.config import Config
    return Config(**item)


def has_recursive_values(obj):
    from fastcfg.config import Config

    if isinstance(obj, dict) or isinstance(obj, Config):
        return True

    return False


def resolve_all_values(obj):
    from fastcfg.config.items import IConfigItem
    from fastcfg.config import Config

    if isinstance(obj, dict):
        obj_dict = obj

    elif isinstance(obj, Config):
        obj_dict = obj.get_dict()

    else:
        raise ValueError(
            'Resolve all values requires obj type to be dict or Config!')

    values = {}

    for k, v in obj_dict.items():
        if has_recursive_values(v):
            v = resolve_all_values(v)

        if isinstance(v, IConfigItem):
            v = v.value

        values[k] = v

    return values
