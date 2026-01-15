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


def apply_pull_payload(
    payload: Mapping[str, Any],
    repos: PullRepositories,
    app_meta_repo: AppMetaRepoPort,
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
    }

    for key, repo in repo_map.items():
        if repo is None:
            continue

        rows = payload.get(key)
        if not rows:
            continue

        repo.upsert_many(rows)

    server_ts = payload.get("server_ts")
    if server_ts:
        app_meta_repo.set_meta("last_pull_at", server_ts)
