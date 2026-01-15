# desktop/tests/e2e/test_e2e_05_company_switch.py

"""
Responsibilities:
- Test e2e 05 company switch behavior.
"""

# desktop/tests/e2e/test_e2e_05_company_switch.py

from desktop.core.bootstrap_service import BootstrapService
from desktop.core.session_service import SessionService
from desktop.core.sync_pull_service import SyncPullService
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection


def test_e2e_05_company_switch(e2e_env):
    """
    E2E-05
    Troca de company não pode misturar dados
    """

    conn = get_connection()

    try:
        repo = ProductsRepo(conn)

        if get_meta("bootstrap_done", conn) != "1":
            BootstrapService().run()

        products_before = repo.get_all(active_only=False)

        # troca company (simulada)
        SessionService.set_company_server_id(9999)

        SyncPullService().run()

        products_after = repo.get_all(active_only=False)

        # não pode misturar dados
        assert products_after == products_before

    finally:
        # restaura company original
        SessionService.set_company_server_id(e2e_env.company_server_id)
        conn.close()
