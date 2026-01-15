# backend/app/services/sync/pull_executor.py

"""
Responsibilities:
- Sync service component for pull executor.
- Coordinate sync workflow steps.
"""

# backend/app/services/sync/pull_executor.py

from datetime import datetime, timezone
from typing import Dict, Any

from app.services.sync.registry import SYNC_HANDLERS


class PullExecutor:
    """
    Executa o pull no DB Server.

    Responsável apenas por:
    - chamar handlers
    - montar payload final
    """

    def execute(
        self,
        *,
        company_server_id: int,
        since: datetime | None,
    ) -> Dict[str, Any]:
        data: Dict[str, list] = {}
        server_ts = datetime.now(timezone.utc).isoformat()

        for entity, handler in SYNC_HANDLERS.items():
            rows = handler.pull(
                company_id=company_server_id,
                since=since,
            )
            for row in rows:
                if isinstance(row, dict) and "server_id" not in row and "id" in row:
                    row["server_id"] = row["id"]
                if isinstance(row, dict):
                    key_map = {
                        "company_id": "company_server_id",
                        "location_id": "location_server_id",
                        "category_id": "category_server_id",
                        "product_id": "product_server_id",
                        "event_id": "event_server_id",
                        "zone_id": "zone_server_id",
                        "user_id": "user_server_id",
                    }
                    for src, dest in key_map.items():
                        if dest not in row and src in row:
                            row[dest] = row[src]
                    if "synced" not in row:
                        row["synced"] = 1
                    if "synced_at" not in row:
                        row["synced_at"] = server_ts
                    if "source" not in row:
                        row["source"] = "server"
            data[entity] = rows

        payload: Dict[str, Any] = {
            "server_ts": server_ts,
        }
        payload.update(data)
        return payload
