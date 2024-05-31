from typing import TYPE_CHECKING, Any, Union

# Import modules directly to avoid circular imports
from fastcfg.config import cfg, items

if TYPE_CHECKING:
    from fastcfg.config.cfg import Config
else:
    Config = None


def create_config_dict(item: dict) -> Config:
    """
    Converts a dictionary into a `Config` object.
    This is abstracted into this module as it's used in multiple places.

    Args:
        item (dict): The dictionary to be converted.

    Returns:
        Config: A `Config` object initialized with the dictionary's key-value pairs.
    """

    return cfg.Config(**item)


def has_recursive_values(obj: Any) -> bool:
    """
    Checks if the given object is a dictionary or a `Config` object. For use in `resolve_all_values`.

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a dictionary or a `Config` object, False otherwise.
    """

    if isinstance(obj, dict) or isinstance(obj, cfg.Config):
        return True

    return False


def resolve_all_values(obj: Union[dict, Config]) -> dict:
    """
    Recursively resolves all values in a dictionary or `Config` object.

    This function traverses the given object, resolving any nested dictionaries or `Config` objects,
    and extracting the values of `IConfigItem` instances.

    Args:
        obj (Union[dict, Config]): The object to resolve.

    Returns:
        dict: A dictionary with all values resolved.

    Raises:
        ValueError: If the object is not a dictionary or `Config` object.
    """

    if isinstance(obj, dict):
        obj_dict = obj

    elif isinstance(obj, cfg.Config):  # Convert Config to dict
        obj_dict = obj.get_dict()

    else:
        raise ValueError("Resolve all values requires obj type to be dict or Config!")

    values = {}

    for k, v in obj_dict.items():
        if has_recursive_values(v):
            v = resolve_all_values(v)  # Recursively resolve values

        if isinstance(v, items.AbstractConfigItem):
            v = v.value

        values[k] = v

    return values
