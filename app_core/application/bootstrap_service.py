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

    def run(self, *, correlation_id: str | None = None) -> None:
        company_server_id = self._session.get_company_server_id()
        if not company_server_id:
            raise RuntimeError("company_server_id not set for bootstrap")

        key = f"last_server_sync_at:{company_server_id}"
        self._app_meta_repo.set_meta(key, "")
        self._app_meta_repo.set_meta("last_pull_at", "")
        self._app_meta_repo.set_meta("bootstrap_done", "0")
        self._sync_pull_service.run(correlation_id=correlation_id)
        self._app_meta_repo.set_meta("bootstrap_done", "1")
