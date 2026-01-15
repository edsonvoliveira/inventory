# desktop/core/bootstrap_service.py

"""
Responsibilities:
- Service layer for bootstrap workflows.
- Coordinate related operations and dependencies.
"""

from desktop.app_core_container import build_services
from desktop.core.session_service import SessionService


class BootstrapService:
    """
    Bootstrap wrapper delegating to app_core.
    """

    def run(self) -> None:
        services = build_services()
        services.bootstrap.run()


def run_bootstrap(jwt_token: str) -> bool:
    if not jwt_token:
        raise RuntimeError("JWT token not available for bootstrap")

    SessionService.set_jwt_token(jwt_token)
    BootstrapService().run()
    return True
