from fastcfg.config import Config

import yaml


def from_yaml(path: str) -> Config:
    with open(path, 'r') as stream:
        try:
            data = yaml.safe_load(stream)

            return Config(**data)
        except yaml.YAMLError as exc:
            print(exc)
