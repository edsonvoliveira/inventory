# backend/app/schemas/auth.py

"""
Responsibilities:
- Pydantic schemas for auth data.
- Define request and response shapes.
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: int | None = None

