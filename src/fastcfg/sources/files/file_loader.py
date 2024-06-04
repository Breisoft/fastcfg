import os
from abc import ABC, abstractmethod
from typing import IO, Any

from fastcfg.config.utils import create_config_dict
from fastcfg.exceptions import FileReadError


class AbstractFileReader(ABC):

    def __init__(
        self,
        file_path: os.PathLike,
        mode: str = "r",
        encoding: str = "utf-8",
    ):

        self._file_path = file_path
        self._mode = mode
        self._encoding = encoding

    def stream_file(self) -> IO[Any]:
        """Opens the file at the given path and returns the file stream."""
        try:
            return open(self._file_path, self._mode, encoding=self._encoding)
        except Exception as exc:
            raise FileReadError from exc

    def convert_data(self, data: Any) -> Any:

        if isinstance(data, dict):
            return create_config_dict(data)

        return data

    @abstractmethod
    def process_raw_stream(self, stream: IO[Any]) -> Any:
        pass

    def get_data(self) -> Any:
        stream = self.stream_file()
        data = self.process_raw_stream(stream)

        # Make sure to close the stream at the end
        stream.close()

        return self.convert_data(data)
