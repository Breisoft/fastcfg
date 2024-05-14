import time
import functools
import random


def exponential_backoff(max_retries=5, base_delay=1, max_delay=32, factor=2, jitter=True):
    """
    Decorator for exponential backoff retries.

    Args:
        max_retries (int): Maximum number of retry attempts.
        base_delay (int): Initial delay between retries in seconds.
        max_delay (int): Maximum delay between retries in seconds.
        factor (int): Multiplicative factor for delay growth.
        jitter (bool): If True, adds a random jitter to the delay.

    Returns:
        function: Wrapped function with retry mechanism.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    sleep_time = delay * (factor ** attempt)
                    if jitter:
                        sleep_time = min(sleep_time, max_delay) * \
                            (0.5 + random.random() / 2)
                    else:
                        sleep_time = min(sleep_time, max_delay)
                    time.sleep(sleep_time)
            return func(*args, **kwargs)
        return wrapper
    return decorator
