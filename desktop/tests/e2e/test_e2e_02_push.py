# desktop/tests/e2e/test_e2e_02_push.py

"""
Responsibilities:
- Test e2e 02 push behavior.
"""

# desktop/tests/e2e/test_e2e_02_push.py

from uuid import uuid4

from desktop.app_core_container import build_services
from desktop.data.repositories.products_repo import ProductsRepo
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
        unique_suffix = str(uuid4())[:8]
        record_uuid = repo.create({
            "name": f"Produto E2E Push {unique_suffix}",
            "sku": f"E2E-PUSH-{unique_suffix}",
            "uom_base": "unit",
            "uom_inventory": "unit",
            "is_active": 1,
            "source": "desktop",
            "synced": 0,
        })

        conn.commit()

        # sanity check
        product = repo.get_by_uuid(record_uuid)
        assert product["synced"] == 0

        # ACT → push
        build_services().sync_push.run()

        # ASSERT → produto marcado como sincronizado
        product = repo.get_by_uuid(record_uuid)
        assert product["synced"] == 1
        assert product["uuid"] == record_uuid

    finally:
        conn.close()

