"""RFC 8785 JSON; reject values that cannot round-trip across Python/JS."""

import hashlib
import json
import math

import rfc8785


def validate_tree(value, depth=0):
    if depth > 64:
        raise ValueError("JSON nesting exceeds supported bound")
    if isinstance(value, str):
        value.encode("utf-8", errors="strict")
    elif isinstance(value, bool) or value is None:
        pass
    elif isinstance(value, int):
        if abs(value) > 9007199254740991:
            raise ValueError("Unsafe JSON integer")
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Nonfinite JSON number")
        if value.is_integer() and abs(value) > 9007199254740991:
            raise ValueError("Unsafe JSON integer")
    elif isinstance(value, list):
        for item in value:
            validate_tree(item, depth + 1)
    elif isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError("JSON key must be text")
            validate_tree(k, depth + 1)
            validate_tree(v, depth + 1)
    else:
        raise ValueError("Unsupported JSON type")


def canonical(value):
    validate_tree(value)
    return rfc8785.dumps(value)


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Nonfinite JSON constant")

    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    except RecursionError:
        raise ValueError("JSON nesting exceeds supported bound") from None
    validate_tree(value)
    return value
