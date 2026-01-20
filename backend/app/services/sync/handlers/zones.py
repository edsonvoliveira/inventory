# backend/app/services/sync/handlers/zones.py

"""
Responsibilities:
- Sync handler for zones entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/zones.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.services.sync.handlers._helpers import record_exists_by_uuid, should_apply_lww, resolve_fk_id
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class ZoneSyncHandler(BaseSyncHandler):
    table_name = "zones"

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
            .select(
                "*, inventory_events!inner(company_id)"
            )
            .eq("inventory_events.company_id", company_id)
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

        event_id = resolve_fk_id(
            sb,
            table_name="inventory_events",
            record_id=payload.get("event_id", payload.get("event_server_id")),
            record_uuid=payload.get("event_uuid"),
            company_id=user.company_server_id,
            require_active=True,
            field="event_id",
        )

        data = {
            "uuid": record_uuid,
            "event_id": int(event_id),   # server_id do inventory_event
            "name": payload["name"],
            "description": payload.get("description"),
            "count_status": payload.get("count_status", "not_started"),
            "lock_status": payload.get("lock_status", "unlocked"),
            "is_active": payload.get("is_active", True),
        }

        sb.table("zones").insert(data).execute()

    # ---------------------------
    # PUSH (UPDATE)
    # ---------------------------
    def update(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()
        if not should_apply_lww(sb, self.table_name, record_uuid, payload.get("client_updated_at")):
            return

        if payload.get("count_status") == "finished":
            zone_resp = (
                sb.table("zones")
                .select("id, event_id")
                .eq("uuid", record_uuid)
                .limit(1)
                .execute()
            )
            zone_data = zone_resp.data or []
            if not zone_data or not isinstance(zone_data[0], dict):
                raise RuntimeError("zone nao encontrada")
            zone_row = zone_data[0]
            zone_id = int(zone_row["id"])
            event_id = int(zone_row["event_id"])

            event_resp = (
                sb.table("inventory_events")
                .select("required_counts")
                .eq("id", event_id)
                .limit(1)
                .execute()
            )
            event_data = event_resp.data or []
            required_counts = 1
            if event_data and isinstance(event_data[0], dict):
                raw_required = event_data[0].get("required_counts", 1)
                try:
                    required_counts = int(raw_required)
                except (TypeError, ValueError):
                    required_counts = 1

            progress_resp = (
                sb.table("zone_user_progress")
                .select("id")
                .eq("zone_id", zone_id)
                .eq("is_finished", True)
                .eq("count_type", "primary")
                .execute()
            )
            progress_data = progress_resp.data or []
            finished_counts = len([row for row in progress_data if isinstance(row, dict)])
            if finished_counts < required_counts:
                raise RuntimeError("ZONE_REQUIRED_COUNTS_NOT_MET")

        self._reject_unknown_fields(payload, allowed_fields=[
            "name",
            "description",
            "count_status",
            "lock_status",
            "is_active",
            "client_updated_at",
        ])

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
            raise RuntimeError("Nenhum campo valido para update de zone")

        sb.table("zones").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ---------------------------
    # PUSH (DELETE)
    # ---------------------------
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()

        sb.table("zones").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
