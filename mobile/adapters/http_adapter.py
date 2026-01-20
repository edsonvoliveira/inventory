from __future__ import annotations

import os
from typing import Mapping, Any, Optional

import requests

from app_core.ports.http_port import HttpPort


DEFAULT_TIMEOUT = 10


class MobileHttpAdapter(HttpPort):
    def get(
        self,
        path: str,
        token: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Mapping[str, Any]:
        url = _build_url(path)
        try:
            resp = requests.get(
                url,
                headers=_headers(token, headers),
                params=dict(params or {}),
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise RuntimeError("Nao foi possivel conectar ao servidor.") from exc

        if not (200 <= resp.status_code < 300):
            raise RuntimeError("Servidor retornou erro ao processar a requisicao.")

        if resp.status_code == 204 or not resp.content:
            return {}

        return resp.json()

    def post(
        self,
        path: str,
        token: str,
        json: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Mapping[str, Any]:
        url = _build_url(path)
        try:
            resp = requests.post(
                url,
                headers=_headers(token, headers),
                json=dict(json or {}),
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise RuntimeError("Nao foi possivel conectar ao servidor.") from exc

        if not (200 <= resp.status_code < 300):
            raise RuntimeError("Servidor retornou erro ao processar a requisicao.")

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


def _headers(jwt_token: str, extra_headers: Optional[Mapping[str, str]] = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(dict(extra_headers))
    return headers
