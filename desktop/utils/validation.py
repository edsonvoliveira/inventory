# desktop/utils/validation.py

"""
Responsibilities:
- Utility helpers for validation.
- Provide shared helper functions.
"""

def is_required(value: str) -> bool:
    return bool(value and value.strip())


def parse_float(value: str):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return None
