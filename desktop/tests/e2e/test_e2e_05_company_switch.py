# desktop/tests/e2e/test_e2e_05_company_switch.py

"""
Responsibilities:
- Test e2e 05 company switch behavior.
"""

# desktop/tests/e2e/test_e2e_05_company_switch.py

from desktop.app_core_container import build_services
from desktop.core.session_service import SessionService
from desktop.bootstrap.bootstrap import wipe_local_database
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repositories.app_meta_repo import get_meta, set_meta
from desktop.data.db.connection import get_connection


def test_e2e_05_company_switch(e2e_env, e2e_clean_db):
    """
    E2E-05
    Troca de company não pode misturar dados
    """

    conn = e2e_clean_db
    try:
        repo = ProductsRepo(conn)

        if get_meta("bootstrap_done", conn) != "1":
            build_services().bootstrap.run()

        products_before = repo.get_all(active_only=False)
        local_uuid = repo.create({
            "name": "Produto Local",
            "sku": "LOCAL-001",
            "uom_base": "unit",
            "uom_inventory": "unit",
            "is_active": 1,
            "source": "desktop",
            "synced": 0,
        })
        conn.commit()

        # simula troca de company forçando wipe completo
        set_meta("company_id", "9999", conn)
        set_meta("bootstrap_done", "1", conn)
        conn.commit()

        conn.close()
        conn = None
        wipe_local_database()
        SessionService.set_jwt_token(e2e_env.jwt_token)
        SessionService.set_company_server_id(e2e_env.company_server_id)
        build_services().bootstrap.run()

        conn = get_connection()
        repo = ProductsRepo(conn)

        products_after = repo.get_all(active_only=False)

        # dado local anterior não pode permanecer
        after_uuids = {p["uuid"] for p in products_after}
        assert local_uuid not in after_uuids

    finally:
        # restaura company original
        SessionService.set_company_server_id(e2e_env.company_server_id)
        if conn:
            conn.close()
