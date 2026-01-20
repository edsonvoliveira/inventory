# backend/app/services/sync/handlers/zone_user_progress.py

"""
Responsibilities:
- Sync handler for zone user progress entities.
- Implement pull and push operations.
"""

#backend/app/services/sync/handlers/zone_user_progress.py

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.services.sync.handlers.base import BaseSyncHandler
from app.services.sync.handlers._helpers import record_exists_by_uuid, should_apply_lww, resolve_fk_id, resolve_zone_id
from app.core.user_context import UserContext
from app.clients.supabase_client import get_supabase_service_client
from app.services.sync.handlers._time import normalize_ts

class ZoneUserProgressHandler(BaseSyncHandler):
    table_name = "zone_user_progress"

    # ---------------------------
    # PULL (Server -> Desktop)
    # ---------------------------
    def pull(
        self,
        *,
        company_id: int,
        since: Optional[datetime],
    ) -> list[dict[str, Any]]:
        supabase = get_supabase_service_client()

        query = (
            supabase
            .table(self.table_name)
            .select(
                "*, zones!inner(id, inventory_events!inner(company_id))"
            )
            .eq("zones.inventory_events.company_id", company_id)
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
    def insert(
        self,
        *,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        supabase = get_supabase_service_client()
        zone_id = resolve_zone_id(
            supabase,
            zone_id=payload.get("zone_id", payload.get("zone_server_id")),
            zone_uuid=payload.get("zone_uuid"),
            company_id=user.company_server_id,
            field="zone_id",
        )
        user_id = resolve_fk_id(
            supabase,
            table_name="users",
            record_id=payload.get("user_id", payload.get("user_server_id")),
            record_uuid=payload.get("user_uuid"),
            company_id=user.company_server_id,
            require_active=True,
            field="user_id",
        )
        count_type = payload.get("count_type")
        started_at = payload.get("started_at")
        device_id = payload.get("device_id")
        if not count_type:
            raise RuntimeError("count_type ausente ou invalido")
        if not started_at:
            raise RuntimeError("started_at ausente ou invalido")
        if not device_id:
            raise RuntimeError("device_id ausente ou invalido")

        data: Dict[str, Any] = {
            "uuid": record_uuid,
            "zone_id": zone_id,
            "user_id": user_id,
            "count_type": count_type,
            "started_at": normalize_ts(started_at, field="started_at"),
            "device_id": device_id,
        }

        optional_fields = [
            "items_counted",
            "qty_total",
            "is_finished",
            "finished_at",
        ]
        for field in optional_fields:
            if field in payload:
                value = payload[field]
                if field == "finished_at":
                    value = normalize_ts(value, field="finished_at")
                data[field] = value

        if record_exists_by_uuid(supabase, self.table_name, record_uuid):
            return
        supabase.table(self.table_name).insert(data).execute()

    # ---------------------------
    # PUSH (UPDATE)
    # ---------------------------
    def update(
        self,
        *,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        supabase = get_supabase_service_client()
        if not should_apply_lww(supabase, self.table_name, record_uuid, payload.get("client_updated_at")):
            return

        allowed_fields = [
            "items_counted",
            "qty_total",
            "is_finished",
            "finished_at",
        ]
        self._reject_unknown_fields(payload, allowed_fields=allowed_fields + ["client_updated_at"])
        data = {k: payload[k] for k in allowed_fields if k in payload}
        if not data:
            raise RuntimeError("Nenhum campo valido para update de progress")

        if "finished_at" in data:
            data["finished_at"] = normalize_ts(data["finished_at"], field="finished_at")

        supabase.table(self.table_name).update(data).eq(
            "uuid", record_uuid
        ).execute()

