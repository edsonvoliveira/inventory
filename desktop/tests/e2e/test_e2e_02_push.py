# desktop/tests/e2e/test_e2e_02_push.py

from desktop.core.sync_push_service import SyncPushService
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.db.connection import get_connection


def test_e2e_02_push_insert(e2e_env):
    """
    E2E-02
    Desktop cria registro local → envia para o servidor (push insert)
    """

    conn = get_connection()

    try:
        repo = ProductsRepo(conn)

        # cria produto local (offline)
        local_id = repo.create({
            "name": "Produto E2E Push",
            "sku": "E2E-PUSH-001",
            "is_active": 1,
            "source": "desktop",
            "synced": 0,
        })

        conn.commit()

        # sanity check
        product = repo.get_by_id(local_id)
        assert product["synced"] == 0

        # ACT → push
        SyncPushService().run()

        # ASSERT → produto marcado como sincronizado
        product = repo.get_by_id(local_id)
        assert product["synced"] == 1
        assert product["server_uuid"] is not None

    finally:
        conn.close()

