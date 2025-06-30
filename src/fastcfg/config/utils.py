from typing import TYPE_CHECKING, Any, Union

# Import modules directly to avoid circular imports
from fastcfg.config import cfg, items, value_wrapper

if TYPE_CHECKING:
    from fastcfg.config.cfg import Config
else:
    Config = None


def create_config_dict(item: dict) -> Config:
    """
    Converts a dictionary (including a ValueWrapped dictionary) into a `Config` object.
    This is abstracted into this module as it's used in multiple places.

    Args:
        item (dict): The dictionary to be converted.

    Returns:
        Config: A `Config` object initialized with the dictionary's key-value pairs.
    """

    if isinstance(item, value_wrapper.ValueWrapper):  # Unwrap ValueWrapper
        item = value_wrapper.ValueWrapper.unwrap(item)

    return cfg.Config(**item)


def potentially_has_children(obj: Any) -> bool:
    """
    Checks if the given object is potentially has children. Currently dict and
    `Config` instances are considered to have children.

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object type is in `POTENTIALLY_HAS_CHILDREN`, False otherwise.
    """

    POTENTIALLY_HAS_CHILDREN = (dict, cfg.Config)

    return isinstance(obj, POTENTIALLY_HAS_CHILDREN)


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
        obj_dict = obj.to_dict()

    else:
        raise ValueError(
            "Resolve all values requires obj type to be dict or Config!"
        )

    values = {}

    for k, v in obj_dict.items():
        if potentially_has_children(v):
            v = resolve_all_values(v)  # Recursively resolve values

        if isinstance(v, items.AbstractConfigItem):
            v = v.value

        values[k] = v

    return values


def deep_merge_config(target, updates):
    """
    Recursively merge updates into target, preserving existing nested values.
    
    This function performs a deep merge where:
    - Existing nested Config objects are recursively updated
    - New keys are added
    - Existing non-Config values are replaced
    - Dictionaries are automatically converted to Config objects
    
    Args:
        target: The target Config object to update
        updates: Dictionary of updates to apply
    """
    for key, value in updates.items():
        # Check if the key already exists in the target
        if hasattr(target, key):
            existing = getattr(target, key)
            
            # If both existing and new value are dict-like, merge recursively
            if isinstance(existing, cfg.Config) and isinstance(value, dict):
                deep_merge_config(existing, value)
            else:
                # Otherwise, replace the value (convert dict to Config if needed)
                if isinstance(value, dict):
                    value = create_config_dict(value)
                setattr(target, key, value)
        else:
            # New key, just set it (convert dict to Config if needed)
            if isinstance(value, dict):
                value = create_config_dict(value)
            setattr(target, key, value)
