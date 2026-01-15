# backend/app/services/sync/handlers/companies.py

"""
Responsibilities:
- Sync handler for companies entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/companies.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class CompanySyncHandler(BaseSyncHandler):
    table_name = "companies"

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
            .eq("id", company_id)
        )

        if since is not None:
            if since.tzinfo is None:
                since = since.replace(tzinfo=timezone.utc)
            query = query.gte("updated_at", since.astimezone(timezone.utc).isoformat())

        result = query.execute()
        data = result.data or []

        out: List[Dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if "server_id" not in item and "id" in item:
                item["server_id"] = item["id"]
            out.append(item)
        return out

    # ---------------------------
    # PUSH (NOT SUPPORTED)
    # ---------------------------
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        raise RuntimeError("Companies n\u00e3o suportam push via sync")

    def update(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        raise RuntimeError("Companies n\u00e3o suportam push via sync")

    def delete(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        raise RuntimeError("Companies n\u00e3o suportam push via sync")
