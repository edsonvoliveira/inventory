from __future__ import annotations

import os
from typing import Mapping, Any, Optional

import requests

from app_core.ports.http_port import HttpPort


class MobileHttpAdapter(HttpPort):
    def get(
        self,
        path: str,
        token: str,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        url = _build_url(path)
        try:
            resp = requests.get(
                url,
                headers=_headers(token),
                params=dict(params or {}),
                timeout=10,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Server request failed (GET {url}): {exc}") from exc

        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"Server error {resp.status_code} (GET {url}): {resp.text}")

        if resp.status_code == 204 or not resp.content:
            return {}

        return resp.json()

    def post(
        self,
        path: str,
        token: str,
        json: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        url = _build_url(path)
        try:
            resp = requests.post(
                url,
                headers=_headers(token),
                json=dict(json or {}),
                timeout=10,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Server request failed (POST {url}): {exc}") from exc

        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"Server error {resp.status_code} (POST {url}): {resp.text}")

        if resp.status_code == 204 or not resp.content:
            return {}

        return resp.json()


def _base_url() -> str:
    base = os.getenv("DV_SERVER_BASE_URL", "http://127.0.0.1:8000")
    return base.rstrip("/")


def _build_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return f"{_base_url()}{path}"


def _headers(jwt_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
