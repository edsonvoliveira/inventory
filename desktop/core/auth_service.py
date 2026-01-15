# desktop/core/auth_service.py

"""
Responsibilities:
- Service layer for auth workflows.
- Coordinate related operations and dependencies.
"""

from desktop.core.auth_session import AuthSession


class AuthService:
    def authenticate(self, email: str, password: str) -> bool:
        AuthSession().login(email, password)
        return True
