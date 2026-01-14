"""Utility functions for the distributed system."""

import time
import uuid
import hashlib
from typing import Dict, Any, Optional


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def generate_transaction_id() -> str:
    """Generate a transaction ID."""
    return f"TXN_{uuid.uuid4().hex[:12]}"


def current_timestamp() -> float:
    """Get current timestamp."""
    return time.time()


def calculate_hash(data: str) -> str:
    """Calculate SHA-256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get nested dictionary value using dot notation."""
    keys = key_path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def set_nested_value(data: Dict[str, Any], key_path: str, value: Any) -> None:
    """Set nested dictionary value using dot notation."""
    keys = key_path.split('.')
    for key in keys[:-1]:
        if key not in data:
            data[key] = {}
        data = data[key]
    data[keys[-1]] = value
