# desktop/tests/e2e/test_e2e_06_resilience.py

from desktop.core.sync_pull_service import SyncPullService
from desktop.core.sync_push_service import SyncPushService
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.db.connection import get_connection


def test_e2e_06_resilience_idempotent(e2e_env):
    """
    E2E-06
    Rodar push/pull múltiplas vezes não duplica dados
    """

    conn = get_connection()

    try:
        repo = ProductsRepo(conn)

        initial_count = len(repo.get_all(active_only=False))

        SyncPullService().run()
        SyncPullService().run()
        SyncPushService().run()
        SyncPushService().run()

        final_count = len(repo.get_all(active_only=False))

        assert final_count == initial_count

    finally:
        conn.close()
