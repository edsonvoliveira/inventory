from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any, Optional

from app_core.ports.repositories.app_meta_repo_port import AppMetaRepoPort
from app_core.ports.repositories.companies_repo_port import CompaniesRepoPort
from app_core.ports.repositories.users_repo_port import UsersRepoPort
from app_core.ports.repositories.devices_repo_port import DevicesRepoPort
from app_core.ports.repositories.product_categories_repo_port import ProductCategoriesRepoPort
from app_core.ports.repositories.products_repo_port import ProductsRepoPort
from app_core.ports.repositories.product_barcodes_repo_port import ProductBarcodesRepoPort
from app_core.ports.repositories.locations_repo_port import LocationsRepoPort
from app_core.ports.repositories.zones_repo_port import ZonesRepoPort
from app_core.ports.repositories.inventory_events_repo_port import InventoryEventsRepoPort
from app_core.ports.repositories.inventory_event_targets_repo_port import InventoryEventTargetsRepoPort
from app_core.ports.repositories.inventory_items_repo_port import InventoryItemsRepoPort
from app_core.ports.repositories.zone_user_progress_repo_port import ZoneUserProgressRepoPort


@dataclass(frozen=True)
class PullRepositories:
    companies: Optional[CompaniesRepoPort] = None
    users: Optional[UsersRepoPort] = None
    devices: Optional[DevicesRepoPort] = None
    product_categories: Optional[ProductCategoriesRepoPort] = None
    products: Optional[ProductsRepoPort] = None
    product_barcodes: Optional[ProductBarcodesRepoPort] = None
    locations: Optional[LocationsRepoPort] = None
    zones: Optional[ZonesRepoPort] = None
    inventory_events: Optional[InventoryEventsRepoPort] = None
    inventory_event_targets: Optional[InventoryEventTargetsRepoPort] = None
    inventory_items: Optional[InventoryItemsRepoPort] = None
    zone_user_progress: Optional[ZoneUserProgressRepoPort] = None


def _company_key(base: str, company_id: Optional[int]) -> str:
    if company_id is None:
        return base
    return f"{base}:{company_id}"


def apply_pull_payload(
    payload: Mapping[str, Any],
    repos: PullRepositories,
    app_meta_repo: AppMetaRepoPort,
    *,
    company_id: Optional[int] = None,
) -> None:
    repo_map = {
        "companies": repos.companies,
        "users": repos.users,
        "devices": repos.devices,
        "product_categories": repos.product_categories,
        "products": repos.products,
        "product_barcodes": repos.product_barcodes,
        "locations": repos.locations,
        "zones": repos.zones,
        "inventory_events": repos.inventory_events,
        "inventory_event_targets": repos.inventory_event_targets,
        "inventory_items": repos.inventory_items,
        "zone_user_progress": repos.zone_user_progress,
    }

    for key, repo in repo_map.items():
        if repo is None:
            continue

        rows = payload.get(key)
        if not rows:
            continue

        sanitized_rows = []
        for row in rows:
            if isinstance(row, dict):
                row = dict(row)
                row.pop("deleted_at", None)
                if "server_id" not in row and "id" in row:
                    row["server_id"] = row["id"]
            sanitized_rows.append(row)

        repo.upsert_many(sanitized_rows)

    server_now = payload.get("server_now") or payload.get("server_ts")
    if server_now:
        app_meta_repo.set_meta(_company_key("last_server_sync_at", company_id), server_now)
        app_meta_repo.set_meta("last_pull_at", server_now)
