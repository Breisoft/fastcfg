"""
FastCFG - Modern configuration management for Python applications.

Created by Josh Breidinger (2025)
Author: Josh Breidinger
Email: company@breisoft.com
GitHub: https://github.com/breisoft

Born from the frustration of serverless configuration hell,
FastCFG makes config management simple, fast, and reliable.
"""


from fastcfg.config.cfg import Config

# Global config object
config = Config()

from typing import Any, Callable, Optional, Union
import threading
from fastcfg.config.cfg import AbstractConfigItem


def refresh(target: Union[Config, AbstractConfigItem]):
    """
    Manually refresh a Config or ConfigItem to detect external changes.
    
    Args:
        target: Config object or ConfigItem to refresh
    
    Example:
        # In your own loop
        for _ in range(60):
            refresh(config.my_var)  # Triggers change detection
            time.sleep(1)
    """
    if isinstance(target, Config):
        for key in target.keys():
            _ = getattr(target, key, None)
    else:
        _ = target.value

def needs_value(
    func: Callable[..., Any],
    config_value: Any,
    *args: Any,
    verbose: bool = False,
    **kwargs: Any,
) -> Optional[bool]:
    """
    Test whether a function requires explicit .value access or works with FastCFG magic.

    This helper function determines if you can pass a FastCFG config value directly
    to a function, or if you need to use .value to extract the underlying value.
    This is particularly useful for identifying C extensions that require exact types.

    Args:
        func: The function to test compatibility with
        config_value: A FastCFG wrapped value (e.g., config.port)
        *args: Additional positional arguments to pass to func (after config_value)
        verbose: If True, prints diagnostic information about the test
        **kwargs: Keyword arguments to pass to func

    Returns:
        bool or None:
            - False: Function works with FastCFG magic (no .value needed)
            - True: Function requires .value to be called on config_value
            - None: Function doesn't work even with .value (incompatible)

    Example:
        config.size = 10

        # Check if np.zeros needs .value
        if needs_value(np.zeros, config.size):
            arr = np.zeros(config.size.value)
        else:
            arr = np.zeros(config.size)

        # With verbose output for debugging
        needs_value(np.zeros, config.size, verbose=True)
        # Prints: zeros requires .value - use config.size.value
    """
    func_name: str = getattr(func, "__name__", str(func))

    # First, try calling the function with the FastCFG magic value directly
    try:
        # Build arguments with config_value first, then any additional args
        test_args: tuple[Any, ...] = (config_value,) + args
        func(*test_args, **kwargs)

        # Success - the function works with our magic wrapper
        if verbose:
            print(f"{func_name} works with FastCFG magic - no .value needed")
        return False

    except TypeError:
        # The function rejected our ValueWrapper, try with .value
        try:
            test_args = (config_value.value,) + args
            func(*test_args, **kwargs)

            # Success with .value
            if verbose:
                attr_name: str = getattr(
                    config_value._item, "name", "config_value"
                )
                print(
                    f"{func_name} requires .value - use config.{attr_name}.value"
                )
            return True

        except Exception as e:
            # Function doesn't work even with .value
            if verbose:
                print(
                    f"{func_name} appears incompatible: {type(e).__name__}: {e}"
                )
            return None

    except Exception as e:
        # Some other error occurred
        if verbose:
            print(
                f"{func_name} failed with unexpected error: {type(e).__name__}: {e}"
            )
        return None
