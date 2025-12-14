from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


# -----------------------------------------------------------------------------
# Security scheme (Swagger + FastAPI)
# -----------------------------------------------------------------------------
bearer_scheme = HTTPBearer(auto_error=True)


# -----------------------------------------------------------------------------
# DTO do usuário autenticado
# -----------------------------------------------------------------------------
@dataclass
class CurrentUser:
    auth_uid: str
    email: str | None


# -----------------------------------------------------------------------------
# Dependency: valida JWT do Supabase e retorna usuário atual
# -----------------------------------------------------------------------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """
    Extrai o Bearer token, valida no Supabase Auth e retorna o usuário autenticado.
    """

    token = credentials.credentials

    url = f"{settings.SUPABASE_URL}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": settings.SUPABASE_ANON_KEY,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    data = resp.json()

    return CurrentUser(
        auth_uid=data.get("id"),
        email=data.get("email"),
    )
