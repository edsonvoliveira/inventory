from __future__ import annotations

from typing import Protocol, Mapping, Any, Optional


class HttpPort(Protocol):
    def get(
        self,
        path: str,
        token: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Mapping[str, Any]:
        ...

    def post(
        self,
        path: str,
        token: str,
        json: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Mapping[str, Any]:
        ...
