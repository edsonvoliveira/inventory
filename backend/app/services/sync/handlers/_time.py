#backend/app/services/sync/handlers/_time.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def normalize_ts(value: Any, *, field: str) -> str:
    """
    Normalize timestamp payloads to ISO 8601 UTC string.
    Accepts ISO strings or datetime objects. Raises on invalid input.
    """
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str) and value:
        try:
            dt = datetime.fromisoformat(value)
        except ValueError as exc:
            raise RuntimeError(f"{field} invalido") from exc
    else:
        raise RuntimeError(f"{field} invalido")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.isoformat()
