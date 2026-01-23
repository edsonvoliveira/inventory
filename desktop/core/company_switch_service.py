# desktop/core/company_switch_service.py

"""
Responsibilities:
- Service layer for company switch workflows.
- Coordinate related operations and dependencies.
"""

#desktop/core/company_switch_service.py

"""
Responsabilities:
- Handle switching company context in the Desktop application
- Clear local data related to the previous company
- Reinitialize data for the new company (executing bootstrap)
"""

from desktop.core.session_service import SessionService
from desktop.core.bootstrap_service import BootstrapService
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import get_meta, set_meta
from desktop.data.repositories import (
    companies_repo,
    outbox_repo,
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
    zone_user_progress_repo,
)


class CompanySwitchService:

    def switch_to(self, company_server_id: int, company_uuid: str | None = None) -> None:
        if not company_server_id:
            raise ValueError("company_server_id inválido para troca de empresa")

        current_company = SessionService.get_company_server_id()
        conn = get_connection()
        stored_company_id = get_meta("company_id", conn)
        if current_company == company_server_id and stored_company_id == str(company_server_id):
            conn.close()
            return

        try:
            # 1) Atualiza contexto de sessão
            SessionService.set_company_server_id(company_server_id)

            # 2) Limpa flags de sync / bootstrap
            set_meta("company_id", str(company_server_id), conn)
            if company_uuid:
                set_meta("company_uuid", company_uuid, conn)
            set_meta("bootstrap_done", "", conn)
            set_meta("last_server_sync_at", "", conn)
            set_meta("last_pull_at", "", conn)

            # 3) Hard delete de todos os dados locais
            companies_repo.CompaniesRepo(conn).delete_all()
            outbox_repo.OutboxRepo(conn).delete_all()
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
            zone_user_progress_repo.ZoneUserProgressRepo(conn).delete_all()

            conn.commit()
        finally:
            conn.close()

        # 4) Bootstrap completo (abre sua própria conexão internamente)
        BootstrapService().run()
