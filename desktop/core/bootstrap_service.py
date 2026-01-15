# desktop/core/bootstrap_service.py

from desktop.core.sync_pull_service import SyncPullService
from desktop.core.session_service import SessionService
from desktop.data.repositories.app_meta_repo import set_meta
from desktop.data.db.connection import get_connection


class BootstrapService:
    """
    Responsável por inicializar o cache local após login ou troca de empresa.
    """

    def run(self) -> None:
        conn = get_connection()
        try:
            company_server_id = SessionService.get_company_server_id()
            if not company_server_id:
                raise RuntimeError("company_server_id nÆo definido para bootstrap")

            # Bootstrap = pull FULL (sem since)
            # Reset do marcador de pull incremental
            set_meta("last_pull_at", "", conn)

            SyncPullService().run()

            # Marcar bootstrap conclu¡do
            set_meta("bootstrap_done", "1", conn)
        finally:
            conn.close()
