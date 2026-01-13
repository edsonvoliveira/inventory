# backend/app/services/sync/handlers/inventory_events.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class InventoryEventSyncHandler(BaseSyncHandler):
    table_name = "inventory_events"

    # ---------------------------
    # PULL
    # ---------------------------
    def pull(
        self,
        *,
        company_id: int,
        since: Optional[datetime],
    ) -> List[Dict[str, Any]]:

        sb = get_supabase_service_client()

        query = (
            sb.table(self.table_name)
            .select("*")
            .eq("company_id", company_id)
        )

        if since is not None:
            query = query.gte("updated_at", since.astimezone(timezone.utc).isoformat())

        result = query.execute()
        data = result.data or []

        out: List[Dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                out.append(item)
            else:
                # se vier algo inesperado, ignore ou levante erro
                # raise TypeError(f"Unexpected item type: {type(item)}")
                continue
        return out

    # ---------------------------
    # PUSH (INSERT)
    # ---------------------------
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "company_id": user.company_server_id,
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

    # ---------------------------
    # PUSH (DELETE)
    # ---------------------------
    def update(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
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
            .execute()

    # ======================================================
    # SOFT DELETE
    # ======================================================
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()

        sb.table("inventory_events") \
            .update({"is_active": False}) \
            .eq("uuid", record_uuid) \
            .execute()
