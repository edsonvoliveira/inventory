# desktop/core/sync_push_service.py
"""
Responsibilities:
- Orchestrating sync pull
- Getting last sync timestamp (last_pull_at)
- Call endpoint and call apply pull payload
- Update meta
"""

from desktop.core.http_client import get
from desktop.core.sync.apply_pull_payload import apply_pull_payload
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection
from desktop.core.session_service import SessionService


class SyncPullService:
    def run(self) -> None:
        conn = get_connection()

        since = get_meta("last_pull_at", conn)

        params = {}
        if since:
            params["since"] = since

        jwt_token = SessionService.get_jwt_token()
        if not jwt_token:
            raise RuntimeError("JWT token não disponível para sync pull")

        payload = get(
            "/v1/sync/pull",
            jwt_token=jwt_token,
            params=params,
        )

        apply_pull_payload(payload, conn)