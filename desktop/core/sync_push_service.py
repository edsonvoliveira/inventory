# desktop/core/sync_push_service.py

"""
Responsibilities:
- Service layer for sync push workflows.
- Coordinate related operations and dependencies.
"""

from desktop.app_core_container import build_services


class SyncPushService:
    """
    Wrapper delegating sync push to app_core.
    """

    def run(self) -> tuple[int, int]:
        services = build_services()
        return services.sync_push.run()
