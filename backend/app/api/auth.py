# backend/app/api/auth.py

"""
Responsibilities:
- API routes for auth endpoints.
- Handle request validation and responses.
"""

#backend/app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, CurrentUser
from app.schemas.auth import LoginRequest, RefreshRequest, AuthTokenResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

_auth = AuthService()


@router.post("/login", response_model=AuthTokenResponse)
async def login(data: LoginRequest):
    try:
        result = _auth.login(data.email, data.password)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return result


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh(data: RefreshRequest):
    try:
        result = _auth.refresh(data.refresh_token)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return result


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)):
    return {
        "auth_uid": user.auth_uid,
        "email": user.email,
        "user_id": user.db_user_id,
        "company_id": user.company_server_id,
    }

