# mobile/core/result.py

"""
Structured service result for UI consumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    ok: bool
    data: T | None = None
    message: str = ""
    error_code: str | None = None
