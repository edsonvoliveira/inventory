# backend/app/services/sync/devices.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class DeviceSyncHandler(BaseSyncHandler):
    table_name = "devices"

    # ======================================================
    # INSERT
    # ======================================================
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "device_uuid": payload["device_uuid"],   # UUID do dispositivo (mobile/desktop)
            "user_id": user.db_user_id,
            "os": payload.get("os"),
            "app_version": payload.get("app_version"),
            "last_sync_at": payload.get("last_sync_at"),
            "is_blocked": payload.get("is_blocked", False),
            "metadata": payload.get("metadata"),
        }

        sb.table("devices").insert(data).execute()

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        update_data = {}

        allowed_fields = [
            "os",
            "app_version",
            "last_sync_at",
            "is_blocked",
            "metadata",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de device")

        sb.table("devices").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ======================================================
    # SOFT DELETE (opcional)
    # ======================================================
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        sb.table("devices").update(
            {"is_blocked": True}
        ).eq(
            "uuid", record_uuid
        ).execute()
