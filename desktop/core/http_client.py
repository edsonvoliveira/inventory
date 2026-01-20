# desktop/core/http_client.py

"""
Responsibilities:
- Core module for http client.
- Provide shared application logic.
"""

import os
from typing import Any, Optional

import requests

class DVServerError(Exception):
    pass


DEFAULT_TIMEOUT = 10


def _base_url() -> str:
    """
    Base URL do DV Server.
    Configure via variável de ambiente DV_SERVER_BASE_URL.
    Ex: http://127.0.0.1:8000
    """
    base = os.getenv("DV_SERVER_BASE_URL", "http://127.0.0.1:8000")
    return base.rstrip("/")


def _build_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return f"{_base_url()}{path}"


def _headers(jwt_token: str, extra_headers: Optional[dict[str, str]] = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    return headers


def get(
    path: str,
    *,
    jwt_token: str,
    params: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    url = _build_url(path)
    try:
        resp = requests.get(
            url,
            headers=_headers(jwt_token, headers),
            params=params,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise DVServerError("Nao foi possivel conectar ao servidor.") from e

    if not (200 <= resp.status_code < 300):
        raise DVServerError("Servidor retornou erro ao processar a requisicao.")

    # Alguns endpoints podem retornar 204 (sem body)
    if resp.status_code == 204 or not resp.content:
        return {}

    return resp.json()


def post(
    path: str,
    *,
    jwt_token: str,
    json_body: dict[str, Any],
    headers: Optional[dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    url = _build_url(path)
    try:
        resp = requests.post(
            url,
            headers=_headers(jwt_token, headers),
            json=json_body,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise DVServerError("Nao foi possivel conectar ao servidor.") from e

    if not (200 <= resp.status_code < 300):
        raise DVServerError("Servidor retornou erro ao processar a requisicao.")

    if resp.status_code == 204 or not resp.content:
        return {}

    return resp.json()
