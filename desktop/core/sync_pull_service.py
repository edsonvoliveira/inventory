# desktop/core/sync_pull_service.py

"""
Responsibilities:
- Service layer for sync pull workflows.
- Coordinate related operations and dependencies.
"""

from desktop.app_core_container import build_services
from desktop.core.http_client import get
from desktop.core.sync.apply_pull_payload import apply_pull_payload
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection


class SyncPullService:
    """
    Wrapper delegating sync pull to app_core.
    """

    def run(self) -> None:
        services = build_services()
        services.sync_pull.run()


def pull_once(jwt_token: str) -> int:
    """
    Helper for ad-hoc pull tests without touching session state.
    Returns the count of received records in the payload.
    """
    if not jwt_token:
        raise RuntimeError("JWT token not available for sync pull")

    conn = get_connection()
    try:
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
        return sum(len(v) for v in payload.values() if isinstance(v, list))
    finally:
        conn.close()
