import time

from fastcfg import config
from fastcfg.backoff import BackoffPolicy
from fastcfg.cache import Cache
from fastcfg.cache.strategies import TTLCacheStrategy
from fastcfg.config.items import LiveConfigItem
from fastcfg.config.state import AbstractLiveStateTracker


class IncrementStateTracker(AbstractLiveStateTracker):
    """
    A custom state tracker that maintains an internal counter and increments it each time the state is accessed.
    The counter resets after reaching a specified maximum value.
    """

    def __init__(
        self,
        retry: bool = False,
        use_cache: bool = False,
        backoff_policy: BackoffPolicy = None,
        cache: Cache = None,
    ):
        # Initialize the parent class
        super().__init__(retry, use_cache, backoff_policy, cache)
        # Start the counter at 0
        self._val = 0

    def get_state_value(self):
        """
        This method is called to get the current state of the configuration item.
        It increments the internal counter by 1 each time it is called.
        If the counter exceeds 10, it resets to 0.
        Returns the current value of the counter.
        """
        self._val += 1  # Increment the counter
        if self._val > 10:  # Check if the counter exceeds the threshold
            self._val = 0  # Reset the counter
        return self._val  # Return the current counter value


def from_increment_tracker(
    retry: bool = False,
    use_cache: bool = False,
    backoff_policy: BackoffPolicy = None,
    cache: Cache = None,
):
    """
    Factory function to create a LiveConfigItem with an IncrementStateTracker.
    This setup allows the configuration item to dynamically update its value based on the internal state of the tracker.
    """
    return LiveConfigItem(
        IncrementStateTracker(retry, use_cache, backoff_policy, cache)
    )


# Assign the LiveConfigItem to a configuration attribute
config.increment = from_increment_tracker()

# Accessing the configuration attribute to demonstrate how it dynamically updates its value
print(config.increment)  # Output: 1
print(config.increment)  # Output: 2
print(config.increment)  # Output: 3


############ Advanced Usage ############

# Create our own cache with a custom policy
ten_second_ttl = TTLCacheStrategy(seconds=10)
custom_cache = Cache(ten_second_ttl)

config.advanced_increment = from_increment_tracker(
    retry=True,  # Automatically use exponential back off w/ default settings
    use_cache=True,  # Enable cache usage
    cache=custom_cache,  # Use our custom cache
    # backoff_policy=BackoffPolicy(...) # Optionally use a custom backoff policy
)

print(config.advanced_increment)  # Output: 1
print(config.advanced_increment)  # Output: 1 (re-uses cached value)

# Make cache expire by waiting 10 seconds
time.sleep(10)

print(config.advanced_increment)  # Output: 2 (cache expired)
