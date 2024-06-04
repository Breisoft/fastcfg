import os
from typing import IO, Any

from fastcfg.exceptions import MissingDependencyError
from fastcfg.sources.files.file_loader import AbstractFileReader

try:
    import yaml
except ImportError:
    yaml = None


class YamlFileReader(AbstractFileReader):

    def __init__(
        self,
        file_path: os.PathLike,
        mode: str = "r",
        encoding: str = "utf-8",
        *args,
        **kwargs
    ):

        super().__init__(
            file_path=file_path,
            mode=mode,
            encoding=encoding,
        )

        self._callable = callable

        self._file_path = file_path
        self._mode = mode
        self._encoding = encoding

        self._args = args
        self._kwargs = kwargs

    def process_raw_stream(self, stream: IO[Any]) -> Any:
        if not yaml:
            raise MissingDependencyError("PyYAML")

        return yaml.safe_load(stream, *self._args, **self._kwargs)
