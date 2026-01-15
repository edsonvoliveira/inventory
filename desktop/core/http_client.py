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


def _headers(jwt_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }


def get(
    path: str,
    *,
    jwt_token: str,
    params: Optional[dict[str, Any]] = None,
    timeout: int = 10,
) -> dict[str, Any]:
    url = _build_url(path)
    try:
        resp = requests.get(
            url,
            headers=_headers(jwt_token),
            params=params,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise DVServerError(f"DV Server request failed (GET {url}): {e}") from e

    if not (200 <= resp.status_code < 300):
        raise DVServerError(f"DV Server error {resp.status_code} (GET {url}): {resp.text}")

    # Alguns endpoints podem retornar 204 (sem body)
    if resp.status_code == 204 or not resp.content:
        return {}

    return resp.json()


def post(
    path: str,
    *,
    jwt_token: str,
    json_body: dict[str, Any],
    timeout: int = 10,
) -> dict[str, Any]:
    url = _build_url(path)
    try:
        resp = requests.post(
            url,
            headers=_headers(jwt_token),
            json=json_body,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise DVServerError(f"DV Server request failed (POST {url}): {e}") from e

    if not (200 <= resp.status_code < 300):
        raise DVServerError(f"DV Server error {resp.status_code} (POST {url}): {resp.text}")

    if resp.status_code == 204 or not resp.content:
        return {}

    return resp.json()