# backend/app/services/sync/zones.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class ZoneSyncHandler(BaseSyncHandler):
    table_name = "zones"

    # ======================================================
    # INSERT
    # ======================================================
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "event_id": payload["event_id"],   # server_id do inventory_event
            "name": payload["name"],
            "description": payload.get("description"),
            "count_status": payload.get("count_status", "not_started"),
            "lock_status": payload.get("lock_status", "unlocked"),
            "is_active": payload.get("is_active", True),
        }

        sb.table("zones").insert(data).execute()

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        update_data = {}

        allowed_fields = [
            "name",
            "description",
            "count_status",
            "lock_status",
            "is_active",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de zone")

        sb.table("zones").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ======================================================
    # SOFT DELETE
    # ======================================================
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        sb.table("zones").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
