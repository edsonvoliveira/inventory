# desktop/core/sync_pull_service.py

"""
Responsibilities:
- Service layer for sync pull workflows.
- Coordinate related operations and dependencies.
"""

from desktop.core.http_client import get
from desktop.core.sync.apply_pull_payload import apply_pull_payload
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection
from desktop.core.session_service import SessionService


class SyncPullService:
    """
    Orquestra o sync pull incremental.
    Responsabilidade única: buscar dados do servidor e delegar aplicação.
    """

    def run(self) -> None:
        conn = get_connection()
        try:
            jwt_token = SessionService.get_jwt_token()
            if not jwt_token:
                raise RuntimeError("JWT token nÆo dispon¡vel para sync pull")

            since = get_meta("last_pull_at", conn)

            params = {}
            if since:
                params["since"] = since

            payload = get(
                "/v1/sync/pull",
                jwt_token=jwt_token,
                params=params,
            )

            apply_pull_payload(payload, conn)
        finally:
            conn.close()
