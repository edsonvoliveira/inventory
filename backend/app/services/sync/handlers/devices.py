# backend/app/services/sync/handlers/devices.py

"""
Responsibilities:
- Sync handler for devices entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/devices.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.services.sync.handlers._helpers import record_exists_by_uuid, should_apply_lww
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext
from app.services.sync.handlers._time import normalize_ts


class DeviceSyncHandler(BaseSyncHandler):
    table_name = "devices"

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
            .select("*, users!inner(company_id)")
            .eq("users.company_id", company_id)
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

        if "is_blocked" in payload:
            raise RuntimeError("DEVICE_BLOCK_CHANGE_FORBIDDEN")

        if record_exists_by_uuid(sb, self.table_name, record_uuid):
            return

        data = {
            "uuid": record_uuid,
            "device_uuid": payload["device_uuid"],   # UUID do dispositivo (mobile/desktop)
            "user_id": user.db_user_id,
            "os": payload.get("os"),
            "app_version": payload.get("app_version"),
            "last_sync_at": normalize_ts(payload.get("last_sync_at"), field="last_sync_at")
                if payload.get("last_sync_at") else None,
            "is_blocked": False,
            "metadata": payload.get("metadata"),
        }

        sb.table("devices").insert(data).execute()

    # ---------------------------
    # PUSH (UPDATE)
    # ---------------------------
    def update(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()

        if not should_apply_lww(sb, self.table_name, record_uuid, payload.get("last_sync_at")):
            return

        update_data = {}

        allowed_fields = [
            "os",
            "app_version",
            "last_sync_at",
            "metadata",
        ]

        if "is_blocked" in payload:
            raise RuntimeError("DEVICE_BLOCK_CHANGE_FORBIDDEN")

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if "last_sync_at" in update_data and update_data["last_sync_at"]:
            update_data["last_sync_at"] = normalize_ts(
                update_data["last_sync_at"],
                field="last_sync_at",
            )
        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de device")

        sb.table("devices").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ---------------------------
    # PUSH (DELETE)
    # ---------------------------
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        raise RuntimeError("DEVICE_BLOCK_CHANGE_FORBIDDEN")
