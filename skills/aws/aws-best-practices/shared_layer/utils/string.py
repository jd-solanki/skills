import json
from typing import Any


def decode_json_strings(obj: Any) -> Any:
    """Recursively decode any JSON-encoded strings in a dict/list structure."""
    if isinstance(obj, dict):
        return {k: decode_json_strings(v) for k, v in obj.items()}  # type: ignore
    elif isinstance(obj, list):
        return [decode_json_strings(i) for i in obj]  # type: ignore
    elif isinstance(obj, str):
        stripped = obj.strip()
        # Only strings that open like an object/array are candidates — without
        # this guard a plain "123" or "null" would decode into a number/None.
        if stripped and stripped[0] in ("{", "["):
            try:
                parsed = json.loads(stripped)
                return decode_json_strings(parsed)
            except (json.JSONDecodeError, ValueError):
                pass
        return obj
    else:
        return obj
