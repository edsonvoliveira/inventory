# backend/app/services/sync/users.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class UserSyncHandler(BaseSyncHandler):
    table_name = "users"

    # ======================================================
    # INSERT
    # ======================================================
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "company_id": user.company_id,  # 🔒 sempre do JWT
            "email": payload["email"],
            "username": payload.get("username"),
            "name": payload["name"],
            "role": payload.get("role", "auditor"),
            "supabase_auth_id": payload.get("supabase_auth_id"),
            "is_active": payload.get("is_active", True),
        }

        sb.table("users").insert(data).execute()

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        update_data = {}

        allowed_fields = [
            "email",
            "username",
            "name",
            "role",
            "is_active",
            "supabase_auth_id",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de user")

        sb.table("users").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ======================================================
    # SOFT DELETE
    # ======================================================
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        sb.table("users").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
