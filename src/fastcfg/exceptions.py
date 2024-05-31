
class ConfigItemValidationError(Exception):
    """Exception raised when a config item value fails validation."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Validation failed: {message}")


class InvalidOperationError(Exception):
    """Exception raised when an invalid operation is performed."""

    def __init__(self, message: str = "Invalid operation performed."):
        self.message = message
        super().__init__(self.message)


class MissingDependencyError(Exception):
    """Exception raised when a dependency is missing."""

    def __init__(self, dependency: str):
        self.dependency = dependency
        super().__init__(
            f"Dependency '{dependency}' is missing. Please install it.")


class NetworkError(Exception):
    """Exception raised when a config key doesn't exist."""


class FileReadError(Exception):
    """Exception raised when a file cannot be read."""


class MaxRetriesExceededError(Exception):
    """Exception raised when the maximum number of retries is exceeded in exponential backoff."""

    def __init__(self, backoff_policy, total_time_slept: float):
        self._backoff_policy = backoff_policy
        self._total_time_slept = total_time_slept
        super().__init__(
            f"""Backoff failed. Total time slept: {self._total_time_slept} seconds. Policy details: {str(self._backoff_policy)}""")


class MissingConfigKeyError(Exception):
    """Exception raised when a config key doesn't exist."""

    def __init__(self, key):
        self.key = key
        super().__init__(
            f"Config key '{key}' doesn't exist. Please ensure that it's set in your config.")


class MissingCacheKeyError(Exception):
    """Exception raised when a cache key doesn't exist."""

    def __init__(self, key):
        self.key = key
        super().__init__(
            f"Cache key '{key}' not found in cache.")


class MissingEnvironmentVariableError(Exception):
    def __init__(self, key):
        self.key = key
        super().__init__(
            f"Environment variable '{key}' doesn't exist. Please ensure that it's set in your environment.")
