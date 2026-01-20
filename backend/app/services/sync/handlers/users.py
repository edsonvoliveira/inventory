# backend/app/services/sync/handlers/users.py

"""
Responsibilities:
- Sync handler for users entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/users.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.services.sync.handlers._helpers import should_apply_lww
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class UserSyncHandler(BaseSyncHandler):
    table_name = "users"

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
        raise RuntimeError("Users nao suportam insert via sync")

    # ---------------------------
    # PUSH (UPDATE)
    # ---------------------------
    def update(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()

        if not should_apply_lww(sb, self.table_name, record_uuid, payload.get("client_updated_at")):
            return

        self._reject_unknown_fields(payload, allowed_fields=[
            "name",
            "role",
            "is_active",
            "client_updated_at",
        ])

        update_data = {}

        allowed_fields = [
            "name",
            "role",
            "is_active",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de user")

        sb.table("users").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ---------------------------
    # PUSH (DELETE)
    # ---------------------------
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        raise RuntimeError("Users nao suportam delete via sync")
