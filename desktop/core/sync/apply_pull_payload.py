#desktop/core/sync/apply_pull_payload.py
"""
Responsibilities:
- Orchestrating payload application
- Only calling repo.insert many()
- No SQL logic
- No UI knowledge
- No HTTP knowledge
"""

from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repositories.product_categories_repo import ProductCategoriesRepo
from desktop.data.repositories.locations_repo import LocationsRepo
from desktop.data.repositories.zones_repo import ZonesRepo
from desktop.data.repositories.inventory_events_repo import InventoryEventsRepo
from desktop.data.repositories.inventory_event_targets_repo import InventoryEventTargetsRepo
from desktop.data.repositories.product_barcodes_repo import ProductBarcodesRepo
from desktop.data.repositories.devices_repo import DevicesRepo
from desktop.data.repositories.users_repo import UsersRepo
from desktop.data.repositories.companies_repo import CompaniesRepo
from desktop.data.repositories.app_meta_repo import set_meta


def apply_pull_payload(payload: dict, conn) -> None:
    """
    Aplica o payload de sync pull no SQLite local.

    Regras:
    - Nenhuma lógica SQL aqui
    - Toda escrita passa exclusivamente pelos repos
    - Payload sempre representa linhas completas vindas do servidor
    """

    repo_map = {
        "companies": CompaniesRepo,
        "users": UsersRepo,
        "devices": DevicesRepo,
        "product_categories": ProductCategoriesRepo,
        "products": ProductsRepo,
        "product_barcodes": ProductBarcodesRepo,
        "locations": LocationsRepo,
        "zones": ZonesRepo,
        "inventory_events": InventoryEventsRepo,
        "inventory_event_targets": InventoryEventTargetsRepo,
    }

    for key, repo_cls in repo_map.items():
        rows = payload.get(key)
        if not rows:
            continue

        repo = repo_cls(conn)
        repo.upsert_many(rows)

    server_ts = payload.get("server_ts")
    if server_ts:
        set_meta("last_pull_at", server_ts, conn)
