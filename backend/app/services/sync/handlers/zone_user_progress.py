#backend/app/services/sync/handlers/zone_user_progress.py

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.services.sync.handlers.base import BaseSyncHandler
from app.core.user_context import UserContext
from app.clients.supabase_client import get_supabase_service_client

class ZoneUserProgressHandler(BaseSyncHandler):
    table_name = "zone_user_progress"

    # ---------------------------
    # PULL (Server → Desktop)
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
        data = payload.copy()
        data["uuid"] = record_uuid

        supabase = get_supabase_service_client()
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
        data = payload.copy()

        supabase = get_supabase_service_client()
        supabase.table(self.table_name).update(data).eq(
            "uuid", record_uuid
        ).execute()

