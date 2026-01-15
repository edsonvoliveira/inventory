from __future__ import annotations

import time
from typing import Any, Mapping

import requests

from desktop.core.session_service import SessionService
from desktop.core.http_client import DVServerError, _build_url


class AuthSession:
    def _post(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        url = _build_url(path)
        try:
            resp = requests.post(url, json=dict(payload), timeout=10)
        except requests.RequestException as exc:
            raise DVServerError(f"Auth request failed (POST {url}): {exc}") from exc

        if not (200 <= resp.status_code < 300):
            raise DVServerError(f"Auth request error {resp.status_code} (POST {url}): {resp.text}")

        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def login(self, email: str, password: str) -> bool:
        data = self._post("/v1/auth/login", {"email": email, "password": password})
        self._store_tokens(data)
        return True

    def refresh(self) -> str:
        refresh_token = SessionService.get_refresh_token()
        if not refresh_token:
            raise DVServerError("refresh_token not available")
        data = self._post("/v1/auth/refresh", {"refresh_token": refresh_token})
        self._store_tokens(data)
        return SessionService.get_jwt_token() or ""

    def get_valid_access_token(self) -> str | None:
        token = SessionService.get_jwt_token()
        if not token:
            return None

        expires_at = SessionService.get_expires_at()
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
            raise DVServerError("Auth response missing tokens")

        expires_in_int = int(expires_in) if isinstance(expires_in, (int, str)) and str(expires_in).isdigit() else None
        expires_at_int = int(expires_at) if isinstance(expires_at, (int, str)) and str(expires_at).isdigit() else None
        if expires_at_int is None and expires_in_int is not None:
            expires_at_int = int(time.time()) + expires_in_int

        SessionService.set_auth_tokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in_int,
            expires_at=expires_at_int,
        )
