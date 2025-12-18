# backend/app/services/sync/inventory_events.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class InventoryEventSyncHandler(BaseSyncHandler):
    table_name = "inventory_events"

    # ======================================================
    # INSERT
    # ======================================================
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "company_id": user.company_id,
            "location_id": payload["location_id"],  # server_id
            "title": payload["title"],
            "event_type": payload["event_type"],
            "status": payload.get("status", "planned"),
            "required_counts": payload.get("required_counts", 1),
            "required_audits": payload.get("required_audits"),
            "tolerance_percent": payload.get("tolerance_percent"),
            "tolerance_absolute": payload.get("tolerance_absolute"),
            "is_active": True,
        }

        sb.table("inventory_events").insert(data).execute()

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        update_data = {}

        allowed_fields = [
            "title",
            "event_type",
            "status",
            "required_counts",
            "required_audits",
            "tolerance_percent",
            "tolerance_absolute",
            "is_active",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de inventory_event")

        sb.table("inventory_events") \
            .update(update_data) \
            .eq("uuid", record_uuid) \
            .eq("company_id", user.company_id) \
            .execute()

    # ======================================================
    # SOFT DELETE
    # ======================================================
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        sb.table("inventory_events") \
            .update({"is_active": False}) \
            .eq("uuid", record_uuid) \
            .eq("company_id", user.company_id) \
            .execute()
