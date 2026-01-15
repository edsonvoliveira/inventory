from __future__ import annotations

from app_core.ports.session_port import SessionPort
from app_core.ports.repositories.app_meta_repo_port import AppMetaRepoPort
from app_core.application.sync_pull_service import SyncPullService


class BootstrapService:
    def __init__(
        self,
        session: SessionPort,
        app_meta_repo: AppMetaRepoPort,
        sync_pull_service: SyncPullService,
    ) -> None:
        self._session = session
        self._app_meta_repo = app_meta_repo
        self._sync_pull_service = sync_pull_service

    def run(self) -> None:
        company_server_id = self._session.get_company_server_id()
        if not company_server_id:
            raise RuntimeError("company_server_id not set for bootstrap")

        self._app_meta_repo.set_meta("last_pull_at", "")
        self._sync_pull_service.run()
        self._app_meta_repo.set_meta("bootstrap_done", "1")
