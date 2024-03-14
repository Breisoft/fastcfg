from fastcfg import Config


def build(data: list[dict] | dict) -> Config:

    # TODO
    if isinstance(data, list):
        pass

    return Config(**data)
