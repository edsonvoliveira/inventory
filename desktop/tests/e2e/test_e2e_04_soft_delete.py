# desktop/tests/e2e/test_e2e_04_soft_delete.py

from desktop.core.sync_push_service import SyncPushService
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.db.connection import get_connection


def test_e2e_04_soft_delete(e2e_env):
    """
    E2E-04
    Delete local deve virar soft delete no servidor
    """

    conn = get_connection()

    try:
        repo = ProductsRepo(conn)

        record_uuid = repo.create({
            "name": "Produto Delete",
            "sku": "DEL-001",
            "uom_base": "unit",
            "uom_inventory": "unit",
            "is_active": 1,
            "source": "desktop",
            "synced": 0,
        })
        conn.commit()

        # push insert
        SyncPushService().run()

        # soft delete local
        repo.soft_delete(record_uuid)
        conn.commit()

        # push delete
        SyncPushService().run()

        product = repo.get_by_uuid(record_uuid)

        assert product["is_active"] == 0
        assert product["deleted_at"] is not None
        assert product["synced"] == 1

    finally:
        conn.close()
