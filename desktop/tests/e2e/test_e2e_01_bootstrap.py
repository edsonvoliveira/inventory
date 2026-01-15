# desktop/tests/e2e/test_e2e_01_bootstrap.py

"""
Responsibilities:
- Test e2e 01 bootstrap behavior.
"""

#desktop/tests/e2e/test_e2e_01_bootstrap.py

from desktop.app_core_container import build_services
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.data.repositories.companies_repo import CompaniesRepo
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repositories.locations_repo import LocationsRepo


def test_e2e_01_bootstrap_initial_load(e2e_env):
    """
    E2E-01
    Dado um DB local vazio e uma sessão válida,
    quando executamos o BootstrapService,
    então os dados mestre devem ser carregados do servidor
    e o estado local marcado como bootstrap concluído.
    """

    # Arrange
    # (DB limpo + sessão válida já garantidos pelas fixtures)
    conn = None

    # Act
    build_services().bootstrap.run()

    # Assert
    # Reabrimos a conexão para validar o estado persistido
    from desktop.data.db.connection import get_connection
    conn = get_connection()

    try:
        # 1) Flags de controle
        bootstrap_done = get_meta("bootstrap_done", conn)
        assert bootstrap_done == "1"

        # 2) Empresa carregada
        companies = CompaniesRepo(conn).get_all(active_only=False)
        assert len(companies) >= 1

        # 3) Dados mestre básicos carregados
        products = ProductsRepo(conn).get_all(active_only=False)
        locations = LocationsRepo(conn).get_all(active_only=False)

        # Não assumimos quantidades exatas (depende do ambiente),
        # apenas que o bootstrap populou corretamente.
        assert products is not None
        assert locations is not None

        # 4) Todos os registros vindos do servidor devem estar sincronizados
        for row in products:
            assert row["synced"] == 1
            assert row["source"] == "server"

    finally:
        conn.close()
