from __future__ import annotations

from mobile.core.auth_session import AuthSession


class AuthService:
    def authenticate(self, email: str, password: str) -> bool:
        AuthSession().login(email, password)
        return True
