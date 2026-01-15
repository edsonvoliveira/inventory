# desktop/core/auth_service.py

"""
Responsibilities:
- Service layer for auth workflows.
- Coordinate related operations and dependencies.
"""

class AuthService:
    def authenticate(self, email: str, password: str) -> bool:
        return email == "admin" and password == "123"
