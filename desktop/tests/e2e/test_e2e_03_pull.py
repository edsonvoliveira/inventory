# desktop/tests/e2e/test_e2e_03_pull.py

"""
Responsibilities:
- Test e2e 03 pull behavior.
"""

# desktop/tests/e2e/test_e2e_03_pull.py

from desktop.core.bootstrap_service import BootstrapService
from desktop.core.sync_pull_service import SyncPullService
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection


def test_e2e_03_pull_incremental(e2e_env):
    """
    E2E-03
    Pull incremental deve trazer apenas dados novos do servidor
    """

    conn = get_connection()

    try:
        repo = ProductsRepo(conn)

        # garante que bootstrap ja ocorreu
        if get_meta("bootstrap_done", conn) != "1":
            BootstrapService().run()

        last_pull = get_meta("last_pull_at", conn)
        assert last_pull

        # ACT
        SyncPullService().run()

        # ASSERT
        products = repo.get_all(active_only=False)

        assert products is not None
        assert len(products) >= 1

        for p in products:
            assert p["synced"] == 1
            assert p["source"] in ("server", "desktop")

    finally:
        conn.close()
