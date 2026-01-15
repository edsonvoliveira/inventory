# mobile/utils/formatters.py

"""
Responsibilities:
- Utility helpers for formatters.
- Provide shared helper functions.
"""

def format_ts_iso(ts: str) -> str:
    if not ts:
        return ""
    return ts.replace("T", " ")[:19]
