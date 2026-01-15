from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app_core.application.bootstrap_service import BootstrapService
from app_core.application.sync_pull_service import SyncPullService
from app_core.application.sync_push_service import SyncPushService
from app_core.ports.repositories.app_meta_repo_port import AppMetaRepoPort
from app_core.ports.session_port import SessionPort


@dataclass
class SyncResult:
    did_bootstrap: bool
    push_accepted: int
    push_failed: int
    pulled: bool
    error: Optional[str] = None


class SyncService:
    def __init__(
        self,
        session: SessionPort,
        app_meta_repo: AppMetaRepoPort,
        bootstrap_service: BootstrapService,
        sync_pull_service: SyncPullService,
        sync_push_service: SyncPushService,
    ) -> None:
        self._session = session
        self._app_meta_repo = app_meta_repo
        self._bootstrap_service = bootstrap_service
        self._sync_pull_service = sync_pull_service
        self._sync_push_service = sync_push_service

    def run(self) -> SyncResult:
        try:
            jwt_token = self._session.get_jwt_token()
            if not jwt_token:
                raise RuntimeError("JWT token not available for sync")

            company_server_id = self._session.get_company_server_id()
            if not company_server_id:
                raise RuntimeError("company_server_id not set in session")

            bootstrap_done = self._app_meta_repo.get_meta("bootstrap_done")
            if bootstrap_done != "1":
                self._bootstrap_service.run()
                return SyncResult(
                    did_bootstrap=True,
                    push_accepted=0,
                    push_failed=0,
                    pulled=True,
                    error=None,
                )

            push_accepted, push_failed = self._sync_push_service.run()
            self._sync_pull_service.run()

            return SyncResult(
                did_bootstrap=False,
                push_accepted=push_accepted,
                push_failed=push_failed,
                pulled=True,
                error=None,
            )
        except Exception as exc:
            return SyncResult(
                did_bootstrap=False,
                push_accepted=0,
                push_failed=0,
                pulled=False,
                error=str(exc),
            )
