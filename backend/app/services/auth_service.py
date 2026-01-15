# backend/app/services/auth_service.py

"""
Responsibilities:
- Module responsibilities not classified.
"""

from __future__ import annotations

from typing import Any, Mapping

import httpx

from app.core.config import settings


class AuthService:
    def _base_headers(self) -> dict[str, str]:
        return {
            "apikey": settings.SUPABASE_ANON_KEY,
            "Content-Type": "application/json",
        }

    def _post(self, url: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            resp = httpx.post(url, headers=self._base_headers(), json=payload, timeout=10.0)
        except httpx.RequestError as exc:
            raise RuntimeError(f"Auth request failed: {exc}") from exc

        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"Auth request error {resp.status_code}: {resp.text}")

        return resp.json()

    def login(self, email: str, password: str) -> Mapping[str, Any]:
        url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
        return self._post(url, {"email": email, "password": password})

    def refresh(self, refresh_token: str) -> Mapping[str, Any]:
        url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
        return self._post(url, {"refresh_token": refresh_token})

