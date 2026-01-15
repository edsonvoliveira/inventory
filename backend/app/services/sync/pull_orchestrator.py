# backend/app/services/sync/pull_orchestrator.py

"""
Responsibilities:
- Sync service component for pull orchestrator.
- Coordinate sync workflow steps.
"""

# services/sync/pull_orchestrator.py

from datetime import datetime
from typing import Optional, Dict, Any

from app.services.sync.pull_executor import PullExecutor
from app.core.security import CurrentUser


class PullOrchestrator:
    """
    Decide bootstrap vs incremental.
    """

    def __init__(self) -> None:
        self.executor = PullExecutor()

    def run(
        self,
        *,
        company_id: int,
        since: Optional[datetime],
        user: CurrentUser,
    ) -> Dict[str, Any]:
        return self.executor.execute(
            company_server_id=company_id,
            since=since,
        )

