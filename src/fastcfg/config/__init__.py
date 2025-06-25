"""
This module initializes the `fastcfg.config` package, making the `Config` class available for importing.

The `Config` class is designed to manage configuration settings in a structured and flexible manner, supporting dynamic attribute management, nested configurations, validation, and environment-specific configurations.

Usage Example:

    ```python
    from fastcfg.config import Config
    # Initialize a Config object with some settings
    config = Config(database={'host': 'localhost', 'port': 5432})
    # Access configuration values
    print(config.database.host) # Output: localhost
    # Add new configuration attributes
    config.new_attr = 'value'
    print(config.new_attr) # Output: value
    ```
"""

# Make Config available for importing
from fastcfg.config.cfg import Config