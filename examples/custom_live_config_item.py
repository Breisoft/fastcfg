import time

from fastcfg import config
from fastcfg.cache import Cache
from fastcfg.cache.strategies import TTLCacheStrategy
from fastcfg.config.items import LiveConfigItem
from fastcfg.config.state import AbstractLiveStateTracker


class TimeBasedStateTracker(AbstractLiveStateTracker):
    """
    Custom state tracker that updates its state based on the elapsed time since initialization.
    The state is updated to reflect the total time elapsed, changing continuously.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._start_time = time.time()

    def get_state_value(self):
        """
        Retrieves the current state of the configuration item, which is the time elapsed
        since the tracker was initialized.
        """
        return time.time() - self._start_time


def from_time_based_tracker(**kwargs):
    """
    Factory function to create a LiveConfigItem using a TimeBasedStateTracker.
    This allows the configuration item to dynamically update based on the elapsed time.
    """
    return LiveConfigItem(TimeBasedStateTracker(**kwargs))


# Assign the LiveConfigItem to a configuration attribute
config.time_based_increment = from_time_based_tracker()

# Pause to simulate time passing
time.sleep(1)

# Demonstrate how the configuration attribute dynamically updates its value
print(
    "Time-based increment value:", config.time_based_increment
)  # Output varies based on the time elapsed


############ Advanced Usage ############

# Create a cache with a custom TTL policy
ten_second_ttl = TTLCacheStrategy(seconds=10)
custom_cache = Cache(ten_second_ttl)

config.advanced_increment = from_time_based_tracker(
    retry=True,  # Enable automatic retry with exponential backoff (default settings)
    use_cache=True,  # Enable caching of the value
    cache=custom_cache,  # Specify the custom cache to use
    # backoff_policy=BackoffPolicy(...) # Optionally specify a custom backoff policy
)

# Pause to simulate time passing
time.sleep(1)

t = config.advanced_increment  # Access the first time
time.sleep(1)
t2 = config.advanced_increment  # This should retrieve the cached value

# Output: Shows cached values and checks equality
print("Cached values:", t, t2, "Are they equal?", t == t2)

# Wait for the cache to expire
time.sleep(10)

# Access the value after cache expiration
# Output: Shows new value after cache has expired
print("Value after cache expiration:", config.advanced_increment)
