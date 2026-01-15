# backend/app/core/security.py

"""
Responsibilities:
- Core module for security.
- Provide shared application logic.
"""

# backend/app/core/security.py

from dataclasses import dataclass
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.clients.supabase_client import get_supabase_service_client


bearer_scheme = HTTPBearer(auto_error=True)


@dataclass
class CurrentUser:
    auth_uid: str
    email: str | None
    db_user_id: int
    company_server_id: int


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:

    token = credentials.credentials

    # 1️⃣ Validar token no Supabase Auth
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
    auth_uid = data.get("id")
    email = data.get("email")

    # 2️⃣ Resolver user_id interno (DB)
    sb = get_supabase_service_client()

    user_resp = (
        sb.table("users")
        .select("id, company_id")
        .eq("supabase_auth_id", auth_uid)
        .limit(1)
        .execute()
    )

    data = user_resp.data

    if not isinstance(data, list) or len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não registrado no sistema",
        )

    row = data[0]

    if not isinstance(row, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resposta inválida ao resolver usuário",
        )

    raw_user_id = row.get("id")
    raw_company_id = row.get("company_id")

    if not isinstance(raw_user_id, (int, str)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ID inválido do usuário",
        )

    if not isinstance(raw_company_id, (int, str)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="company_id inválido do usuário",
        )

    db_user_id = int(raw_user_id)
    company_server_id = int(raw_company_id)

    return CurrentUser(
        auth_uid=auth_uid,
        email=email,
        db_user_id=db_user_id,
        company_server_id=company_server_id,
    )
