# desktop/core/sync_service.py

"""
Responsibilities:
- Service layer for sync workflows.
- Coordinate related operations and dependencies.
"""

from dataclasses import dataclass
from typing import Optional

from desktop.app_core_container import build_services
from desktop.core.session_service import SessionService
from desktop.core.bootstrap_service import BootstrapService
from desktop.bootstrap.bootstrap import wipe_local_database
from desktop.data.repositories.app_meta_repo import get_meta, set_meta


@dataclass
class SyncResult:
    did_bootstrap: bool
    push_accepted: int
    push_failed: int
    pulled: bool
    error: Optional[str] = None


class SyncService:
    def run(self) -> SyncResult:
        services = build_services()
        result = services.sync.run()
        return SyncResult(
            did_bootstrap=result.did_bootstrap,
            push_accepted=result.push_accepted,
            push_failed=result.push_failed,
            pulled=result.pulled,
            error=result.error,
        )


def ensure_bootstrap_for_company(company_id: int, company_uuid: str) -> bool:
    stored_company_id = get_meta("company_id")
    bootstrap_done = get_meta("bootstrap_done") in {"1", "true"}

    if stored_company_id is None:
        set_meta("company_id", str(company_id))
        set_meta("company_uuid", company_uuid)
        set_meta("bootstrap_done", "false")
        BootstrapService().run()
        return True

    if stored_company_id != str(company_id):
        wipe_local_database()
        set_meta("company_id", str(company_id))
        set_meta("company_uuid", company_uuid)
        set_meta("bootstrap_done", "false")
        BootstrapService().run()
        return True

    if not bootstrap_done:
        BootstrapService().run()
        return True

    return False


def push_outbox_once(jwt_token: str) -> tuple[int, int]:
    if not jwt_token:
        raise RuntimeError("JWT token not available for sync push")

    SessionService.set_jwt_token(jwt_token)
    services = build_services()
    return services.sync_push.run()
