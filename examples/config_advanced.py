from fastcfg import Config
from fastcfg.sources.memory import from_callable

# Initialize a complex nested configuration with multiple levels using Config objects
config = Config(
    main=Config(
        sub=Config(
            key="initial", more_nested=Config(inner_key="initial_inner")
        )
    )
)


# Function to simulate fetching updates from an API for nested configurations
def fetch_config_updates():
    # Simulated API response with nested updates
    return Config(
        sub=Config(
            key="updated", more_nested=Config(inner_key="updated_inner")
        )
    )


# Update configuration dynamically from an API
config.main = from_callable(fetch_config_updates)

# Accessing a deeply nested configuration
print(
    config.main.sub.key
)  # Output should reflect the updated value from the API
print(
    config.main.sub.more_nested.inner_key
)  # Output should reflect the updated inner value from the API

# This example shows real-time updating, nested configurations, and external integration.
