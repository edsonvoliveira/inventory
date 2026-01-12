# backend/app/services/sync/pull_executor.py

from datetime import datetime
from typing import Dict, Any
from datetime import datetime, timezone

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

        for entity, handler in SYNC_HANDLERS.items():
            data[entity] = handler.pull(
                company_id=company_server_id,
                since=since,
            )

        return {
            "server_time": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
