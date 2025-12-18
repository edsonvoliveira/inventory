# backend/app/services/sync/locations.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class LocationSyncHandler(BaseSyncHandler):
    table_name = "locations"

    # ======================================================
    # INSERT
    # ======================================================
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "company_id": user.company_id,
            "code": payload["code"],
            "name": payload["name"],
            "address": payload.get("address"),
            "is_active": payload.get("is_active", True),
        }

        sb.table("locations").insert(data).execute()

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        update_data = {}

        allowed_fields = [
            "code",
            "name",
            "address",
            "is_active",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de location")

        sb.table("locations") \
            .update(update_data) \
            .eq("uuid", record_uuid) \
            .eq("company_id", user.company_id) \
            .execute()

    # ======================================================
    # SOFT DELETE
    # ======================================================
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        sb.table("locations") \
            .update({"is_active": False}) \
            .eq("uuid", record_uuid) \
            .eq("company_id", user.company_id) \
            .execute()
