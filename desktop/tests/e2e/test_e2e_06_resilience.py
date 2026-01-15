# desktop/tests/e2e/test_e2e_06_resilience.py

"""
Responsibilities:
- Test e2e 06 resilience behavior.
"""

# desktop/tests/e2e/test_e2e_06_resilience.py

from desktop.app_core_container import build_services
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
            build_services().bootstrap.run()

        initial_count = len(repo.get_all(active_only=False))

        build_services().sync_pull.run()
        build_services().sync_pull.run()
        build_services().sync_push.run()
        build_services().sync_push.run()

        final_count = len(repo.get_all(active_only=False))

        assert final_count == initial_count

    finally:
        conn.close()
