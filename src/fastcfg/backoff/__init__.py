import time
import functools
import random

from fastcfg.exceptions import MaxRetriesExceededError

from dataclasses import dataclass


@dataclass
class BackoffPolicy:
    max_retries: int
    base_delay: float
    max_delay: float
    factor: float
    jitter: bool


def exponential_backoff(backoff_policy: BackoffPolicy):
    """
    Decorator for exponential backoff retries.

    Args:
        backoff_policy (BackoffPolicy): Configuration object containing:
            - max_retries (int): Maximum number of retry attempts.
            - base_delay (float): Initial delay between retries in seconds.
            - max_delay (float): Maximum delay between retries in seconds.
            - factor (float): Multiplicative factor for delay growth.
            - jitter (bool): If True, adds a random jitter to the delay.

    Returns:
        function: Wrapped function with retry mechanism.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = backoff_policy.base_delay

            total_time_slept = 0

            for attempt in range(backoff_policy.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:

                    if attempt == backoff_policy.max_retries - 1:
                        raise MaxRetriesExceededError(
                            backoff_policy, total_time_slept) from exc

                    sleep_time = delay * (backoff_policy.factor ** attempt)

                    if backoff_policy.jitter:
                        sleep_time = min(sleep_time, backoff_policy.max_delay) * \
                            (0.5 + random.random() / 2)
                    else:
                        sleep_time = min(sleep_time, backoff_policy.max_delay)

                    time.sleep(sleep_time)
                    total_time_slept += sleep_time

            return func(*args, **kwargs)
        return wrapper
    return decorator
