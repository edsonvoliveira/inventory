#desktop/core/company_switch_service.py

"""
Responsabilities:
- Handle switching company context in the Desktop application
- Clear local data related to the previous company
- Reinitialize data for the new company
"""

from desktop.core.session_service import SessionService
from desktop.core.bootstrap_service import BootstrapService
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import set_meta
from desktop.data.repositories import (
    products_repo,
    product_categories_repo,
    locations_repo,
    zones_repo,
    inventory_events_repo,
    inventory_event_targets_repo,
    inventory_items_repo,
    product_barcodes_repo,
    users_repo,
    devices_repo,
)


class CompanySwitchService:
    """
    Troca o contexto de empresa no Desktop:
    - Atualiza sessão
    - Limpa cache local (hard delete administrativo)
    - Executa bootstrap completo
    """

    def switch_to(self, company_server_id: int) -> None:
        if not company_server_id:
            raise ValueError("company_server_id inválido para troca de empresa")

        current_company = SessionService.get_company_server_id()
        if current_company == company_server_id:
            return

        conn = get_connection()
        try:
            # 1) Atualiza contexto de sessão
            SessionService.set_company_server_id(company_server_id)

            # 2) Limpa flags de sync / bootstrap
            set_meta("bootstrap_done", "", conn)
            set_meta("last_pull_at", "", conn)

            # 3) Hard delete de todos os dados locais
            products_repo.ProductsRepo(conn).delete_all()
            product_categories_repo.ProductCategoriesRepo(conn).delete_all()
            locations_repo.LocationsRepo(conn).delete_all()
            zones_repo.ZonesRepo(conn).delete_all()
            inventory_events_repo.InventoryEventsRepo(conn).delete_all()
            inventory_event_targets_repo.InventoryEventTargetsRepo(conn).delete_all()
            inventory_items_repo.InventoryItemsRepo(conn).delete_all()
            product_barcodes_repo.ProductBarcodesRepo(conn).delete_all()
            users_repo.UsersRepo(conn).delete_all()
            devices_repo.DevicesRepo(conn).delete_all()

            conn.commit()
        finally:
            conn.close()

        # 4) Bootstrap completo (abre sua própria conexão internamente)
        BootstrapService().run()