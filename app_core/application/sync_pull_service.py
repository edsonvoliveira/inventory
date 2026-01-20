from __future__ import annotations

from typing import Any, Mapping

from app_core.application.apply_pull_payload import apply_pull_payload, PullRepositories
from app_core.ports.http_port import HttpPort
from app_core.ports.session_port import SessionPort
from app_core.ports.repositories.app_meta_repo_port import AppMetaRepoPort
from app_core.ports.sync_state_port import SyncStatePort


class SyncPullService:
    def __init__(
        self,
        http: HttpPort,
        session: SessionPort,
        app_meta_repo: AppMetaRepoPort,
        repos: PullRepositories,
        sync_state: SyncStatePort | None = None,
    ) -> None:
        self._http = http
        self._session = session
        self._app_meta_repo = app_meta_repo
        self._repos = repos
        self._sync_state = sync_state

    def run(self, *, correlation_id: str | None = None) -> None:
        jwt_token = self._session.get_jwt_token()
        if not jwt_token:
            raise RuntimeError("JWT token not available for sync pull")

        company_id = self._session.get_company_server_id()
        key = f"last_server_sync_at:{company_id}" if company_id else "last_server_sync_at"
        since = self._app_meta_repo.get_meta(key) or self._app_meta_repo.get_meta("last_pull_at")
        params: dict[str, Any] = {}
        if since:
            params["since"] = since

        headers = {}
        if correlation_id:
            headers["X-Correlation-Id"] = correlation_id

        payload = self._http.get(
            "/v1/sync/pull",
            token=jwt_token,
            params=params,
            headers=headers,
        )

        apply_pull_payload(
            payload,
            self._repos,
            self._app_meta_repo,
            company_id=int(company_id) if company_id else None,
        )

        server_now = payload.get("server_now") or payload.get("server_ts")
        if server_now and self._sync_state:
            self._sync_state.set_last_server_sync_at(
                server_now,
                int(company_id) if company_id else None,
            )
