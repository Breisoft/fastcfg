# This file contains utility functions for reading and writing files auto
# parsing based on the file extension (json, yaml, pkl)

import json
import pickle
import os
from typing import Any
from fastcfg.exceptions import MissingDependencyError

# Try to import yaml, but handle missing dependency gracefully
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def file_reader(file_path: str) -> str:
    """
    Read a file and return its contents as a string.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file can't be read
    """
    with open(file_path, "r") as f:
        return f.read()


def file_writer(file_path: str, data: str) -> None:
    """
    Write data to a file.
    
    Args:
        file_path: Path to the file to write
        data: String data to write
        
    Raises:
        IOError: If file can't be written
    """
    with open(file_path, "w") as f:
        f.write(data)


def load_file(file_path: str) -> Any:
    """
    Load and parse a file based on its extension.
    Supports json, yaml, yml, and pkl files.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        Parsed data from the file
        
    Raises:
        ValueError: If file extension is not supported
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON file is invalid
        yaml.YAMLError: If YAML file is invalid
        pickle.UnpicklingError: If pickle file is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.json':
        with open(file_path, 'r') as f:
            return json.load(f)
    elif ext in ('.yaml', '.yml'):
        if not YAML_AVAILABLE:
            raise MissingDependencyError("PyYAML")
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.pkl':
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    else:
        supported = ['.json', '.pkl']
        if YAML_AVAILABLE:
            supported.extend(['.yaml', '.yml'])
        raise ValueError(f"Unsupported file extension: {ext}. Supported: {', '.join(supported)}")


def save_file(file_path: str, data: Any, **kwargs) -> None:
    """
    Save data to a file based on its extension.
    Supports json, yaml, yml, and pkl files.
    
    Args:
        file_path: Path to the file to save
        data: Data to save
        **kwargs: Additional arguments passed to the specific format writer
        
    Raises:
        ValueError: If file extension is not supported
        TypeError: If data can't be serialized
    """
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.json':
        with open(file_path, 'w') as f:
            json.dump(data, f, **kwargs)
    elif ext in ('.yaml', '.yml'):
        if not YAML_AVAILABLE:
            from fastcfg.exceptions import MissingDependencyError
            raise MissingDependencyError("PyYAML")
        with open(file_path, 'w') as f:
            yaml.dump(data, f, **kwargs)
    elif ext == '.pkl':
        with open(file_path, 'wb') as f:
            pickle.dump(data, f, **kwargs)
    else:
        supported = ['.json', '.pkl']
        if YAML_AVAILABLE:
            supported.extend(['.yaml', '.yml'])
        raise ValueError(f"Unsupported file extension: {ext}. Supported: {', '.join(supported)}")


def get_supported_extensions() -> list[str]:
    """
    Get list of supported file extensions.
    
    Returns:
        List of supported file extensions
    """
    return ['.json', '.yaml', '.yml', '.pkl']


def is_supported_extension(file_path: str) -> bool:
    """
    Check if a file path has a supported extension.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if extension is supported, False otherwise
    """
    _, ext = os.path.splitext(file_path.lower())
    return ext in get_supported_extensions()