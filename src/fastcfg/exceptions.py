

class MissingConfigKeyError(Exception):
    """Exception raised when a config key doesn't exist."""

    def __init__(self, key):
        self.key = key
        super().__init__(
            f"Config key '{key}' doesn't exist. Please ensure that it's")
