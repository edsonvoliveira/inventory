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
        .select("id")
        .eq("supabase_auth_id", auth_uid)
        .limit(1)
        .execute()
    )

    if not isinstance(user_resp.data, list) or not user_resp.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não registrado no sistema",
        )

    user_data = user_resp.data

    # 1️⃣ Garantir lista válida
    if not isinstance(user_data, list) or len(user_data) == 0:
        raise RuntimeError("Usuário não encontrado no Supabase")

    raw_user = user_data[0]

    # 2️⃣ Garantir dict
    if not isinstance(raw_user, dict):
        raise RuntimeError("Formato inválido do usuário retornado")

    raw_user_id = raw_user.get("id")

    # 3️⃣ Garantir ID válido
    if not isinstance(raw_user_id, (int, str)):
        raise RuntimeError("ID inválido do usuário")

    db_user_id: int = int(raw_user_id)


    return CurrentUser(
        auth_uid=auth_uid,
        email=email,
        db_user_id=db_user_id,
    )
