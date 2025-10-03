"""
Helper Functions
Location: agribot/utils/helpers.py

Utility functions used throughout the AgriBot application.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

def format_timestamp(dt: datetime = None) -> str:
    """Format datetime as ISO string with timezone"""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback"""
    if not json_str:
        return default
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely dump object to JSON string"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_unique_items(items: List[Any]) -> List[Any]:
    """Extract unique items while preserving order"""
    seen = set()
    unique_items = []
    
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
    
    return unique_items

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage with division by zero protection"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def get_nested_value(data: Dict, keys: str, default: Any = None) -> Any:
    """Get nested dictionary value using dot notation"""
    try:
        value = data
        for key in keys.split('.'):
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def merge_dictionaries(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result