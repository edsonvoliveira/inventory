from __future__ import annotations

import time
from typing import Any, Mapping

import requests

from mobile.data.repositories.app_meta_repo import get_meta, set_meta


class AuthSession:
    def _base_url(self) -> str:
        return get_meta("dv_server_base_url") or "http://127.0.0.1:8000"

    def _post(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        base = self._base_url().rstrip("/")
        url = f"{base}{path if path.startswith('/') else '/' + path}"
        try:
            resp = requests.post(url, json=dict(payload), timeout=10)
        except requests.RequestException as exc:
            raise RuntimeError(f"Auth request failed (POST {url}): {exc}") from exc

        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"Auth request error {resp.status_code} (POST {url}): {resp.text}")

        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def login(self, email: str, password: str) -> bool:
        data = self._post("/v1/auth/login", {"email": email, "password": password})
        self._store_tokens(data)
        return True

    def refresh(self) -> str:
        refresh_token = get_meta("refresh_token")
        if not refresh_token:
            raise RuntimeError("refresh_token not available")
        data = self._post("/v1/auth/refresh", {"refresh_token": refresh_token})
        self._store_tokens(data)
        return get_meta("jwt_token") or ""

    def get_valid_access_token(self) -> str | None:
        token = get_meta("jwt_token")
        if not token:
            return None

        expires_at_raw = get_meta("expires_at")
        expires_at = int(expires_at_raw) if expires_at_raw and str(expires_at_raw).isdigit() else None
        if not expires_at:
            return token

        now = int(time.time())
        if now >= (expires_at - 60):
            return self.refresh()

        return token

    def _store_tokens(self, data: Mapping[str, Any]) -> None:
        access_token = str(data.get("access_token") or "")
        refresh_token = str(data.get("refresh_token") or "")
        expires_in = data.get("expires_in")
        expires_at = data.get("expires_at")

        if not access_token or not refresh_token:
            raise RuntimeError("Auth response missing tokens")

        expires_in_int = int(expires_in) if isinstance(expires_in, (int, str)) and str(expires_in).isdigit() else None
        expires_at_int = int(expires_at) if isinstance(expires_at, (int, str)) and str(expires_at).isdigit() else None
        if expires_at_int is None and expires_in_int is not None:
            expires_at_int = int(time.time()) + expires_in_int

        set_meta("jwt_token", access_token)
        set_meta("refresh_token", refresh_token)
        if expires_in_int is not None:
            set_meta("expires_in", str(expires_in_int))
        if expires_at_int is not None:
            set_meta("expires_at", str(expires_at_int))
