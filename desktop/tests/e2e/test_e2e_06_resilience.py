# desktop/tests/e2e/test_e2e_06_resilience.py

"""
Responsibilities:
- Test e2e 06 resilience behavior.
"""

# desktop/tests/e2e/test_e2e_06_resilience.py

from desktop.core.bootstrap_service import BootstrapService
from desktop.core.sync_pull_service import SyncPullService
from desktop.core.sync_push_service import SyncPushService
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection


def test_e2e_06_resilience_idempotent(e2e_env):
    """
    E2E-06
    Rodar push/pull múltiplas vezes não duplica dados
    """

    conn = get_connection()

    try:
        repo = ProductsRepo(conn)

        if get_meta("bootstrap_done", conn) != "1":
            BootstrapService().run()

        initial_count = len(repo.get_all(active_only=False))

        SyncPullService().run()
        SyncPullService().run()
        SyncPushService().run()
        SyncPushService().run()

        final_count = len(repo.get_all(active_only=False))

        assert final_count == initial_count

    finally:
        conn.close()
