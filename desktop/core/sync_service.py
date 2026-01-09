# desktop/core/sync_service.py
"""
Master synchronization orchestrator.
Responsibilities:
- Validate context (JWT / company)
- Decide between bootstrap and incremental sync
- Execute push and pull in the correct order
- Return results to logs/UI
"""

from dataclasses import dataclass
from typing import Optional

from desktop.core.session_service import SessionService
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection

from desktop.core.sync_pull_service import SyncPullService
from desktop.core.sync_push_service import SyncPushService
from desktop.core.bootstrap_service import BootstrapService


@dataclass
class SyncResult:
    did_bootstrap: bool
    push_accepted: int
    push_failed: int
    pulled: bool
    error: Optional[str] = None


class SyncService:

    def run(self) -> SyncResult:
        try:
            conn = get_connection()

            jwt_token = SessionService.get_jwt_token()
            if not jwt_token:
                raise RuntimeError("JWT token não disponível para sincronização")

            company_server_id = SessionService.get_company_server_id()
            if not company_server_id:
                raise RuntimeError("company_server_id não definido na sessão")

            bootstrap_done = get_meta("bootstrap_done", conn)
            if bootstrap_done != "1":
                BootstrapService().run()
                return SyncResult(
                    did_bootstrap=True,
                    push_accepted=0,
                    push_failed=0,
                    pulled=True,
                    error=None,
                )

            # Ordem recomendada (padrão offline-first):
            # 1) push (publica mudanças locais)
            # 2) pull (traz consolidação do servidor)
            push_accepted, push_failed = SyncPushService().run()

            SyncPullService().run()

            return SyncResult(
                did_bootstrap=False,
                push_accepted=push_accepted,
                push_failed=push_failed,
                pulled=True,
                error=None,
            )

        except Exception as e:
            return SyncResult(
                did_bootstrap=False,
                push_accepted=0,
                push_failed=0,
                pulled=False,
                error=str(e),
            )
