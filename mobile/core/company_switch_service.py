# mobile/core/company_switch_service.py

"""
Responsibilities:
- Handle switching company context in the Mobile application.
- Clear local data related to the previous company.
- Reinitialize data for the new company (executing bootstrap).
"""

from mobile.app_core_container import build_services
from mobile.data.db.connection import get_connection
from mobile.data.repositories.app_meta_repo import get_meta, set_meta


class CompanySwitchService:
    def switch_to(self, company_server_id: int, company_uuid: str | None = None) -> None:
        if not company_server_id:
            raise ValueError("company_server_id invalido para troca de empresa")

        conn = get_connection()
        stored_company_id = get_meta("company_id")
        if stored_company_id == str(company_server_id):
            conn.close()
            return

        try:
            # Atualiza contexto
            set_meta("company_id", str(company_server_id))
            if company_uuid:
                set_meta("company_uuid", company_uuid)
            set_meta("company_server_id", str(company_server_id))
            set_meta("bootstrap_done", "")
            set_meta("last_pull_at", "")
            set_meta(f"last_server_sync_at:{company_server_id}", "")

            # Limpa dados locais
            for table in (
                "outbox_local",
                "inventory_items_local",
                "zone_user_progress_local",
                "inventory_event_targets_local",
                "zones_local",
                "inventory_events_local",
                "product_barcodes_local",
                "products_local",
                "product_categories_local",
                "locations_local",
                "devices_local",
                "users_local",
                "companies_local",
                "sync_state",
            ):
                conn.execute(f"DELETE FROM {table}")
            conn.commit()
        finally:
            conn.close()

        build_services().bootstrap.run()
