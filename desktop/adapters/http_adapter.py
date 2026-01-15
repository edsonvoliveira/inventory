from __future__ import annotations

from typing import Mapping, Any, Optional

from app_core.ports.http_port import HttpPort
from desktop.core import http_client


class DesktopHttpAdapter(HttpPort):
    def get(
        self,
        path: str,
        token: str,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return http_client.get(path, jwt_token=token, params=dict(params or {}))

    def post(
        self,
        path: str,
        token: str,
        json: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return http_client.post(path, jwt_token=token, json_body=dict(json or {}))
