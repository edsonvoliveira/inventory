# backend/app/services/sync/handlers/inventory_events.py

"""
Responsibilities:
- Sync handler for inventory events entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/inventory_events.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.services.sync.handlers._helpers import record_exists_by_uuid, should_apply_lww, resolve_fk_id
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
        if record_exists_by_uuid(sb, self.table_name, record_uuid):
            return

        location_id = resolve_fk_id(
            sb,
            table_name="locations",
            record_id=payload.get("location_id", payload.get("location_server_id")),
            record_uuid=payload.get("location_uuid"),
            company_id=user.company_server_id,
            require_active=True,
            field="location_id",
        )
        data = {
            "uuid": record_uuid,
            "company_id": user.company_server_id,
            "location_id": location_id,  # server_id
            "title": payload["title"],
            "event_type": payload.get("event_type"),
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
        if not should_apply_lww(sb, self.table_name, record_uuid, payload.get("client_updated_at")):
            return

        new_status = payload.get("status")
        if new_status in {"closed", "finalized"}:
            event_resp = (
                sb.table("inventory_events")
                .select("id, company_id")
                .eq("uuid", record_uuid)
                .limit(1)
                .execute()
            )
            event_data = event_resp.data or []
            if not event_data or not isinstance(event_data[0], dict):
                raise RuntimeError("inventory_event nao encontrado")
            event_row = event_data[0]
            if int(event_row.get("company_id", 0)) != int(user.company_server_id):
                raise RuntimeError("inventory_event nao encontrado")
            event_id = int(event_row["id"])

            zones_resp = (
                sb.table("zones")
                .select("id")
                .eq("event_id", event_id)
                .neq("count_status", "finished")
                .execute()
            )
            zones_data = zones_resp.data or []
            has_open_zones = any(isinstance(row, dict) for row in zones_data)
            if has_open_zones:
                raise RuntimeError("EVENT_ZONES_NOT_FINISHED")

        self._reject_unknown_fields(payload, allowed_fields=[
            "title",
            "event_type",
            "status",
            "required_counts",
            "required_audits",
            "tolerance_percent",
            "tolerance_absolute",
            "client_updated_at",
        ])

        update_data = {}

        allowed_fields = [
            "title",
            "event_type",
            "status",
            "required_counts",
            "required_audits",
            "tolerance_percent",
            "tolerance_absolute",
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
