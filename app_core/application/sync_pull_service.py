from __future__ import annotations

from typing import Any, Mapping

from app_core.application.apply_pull_payload import apply_pull_payload, PullRepositories
from app_core.ports.http_port import HttpPort
from app_core.ports.session_port import SessionPort
from app_core.ports.repositories.app_meta_repo_port import AppMetaRepoPort


class SyncPullService:
    def __init__(
        self,
        http: HttpPort,
        session: SessionPort,
        app_meta_repo: AppMetaRepoPort,
        repos: PullRepositories,
    ) -> None:
        self._http = http
        self._session = session
        self._app_meta_repo = app_meta_repo
        self._repos = repos

    def run(self) -> None:
        jwt_token = self._session.get_jwt_token()
        if not jwt_token:
            raise RuntimeError("JWT token not available for sync pull")

        since = self._app_meta_repo.get_meta("last_pull_at")
        params: dict[str, Any] = {}
        if since:
            params["since"] = since

        payload = self._http.get(
            "/v1/sync/pull",
            token=jwt_token,
            params=params,
        )

        apply_pull_payload(payload, self._repos, self._app_meta_repo)
