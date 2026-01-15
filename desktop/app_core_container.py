from __future__ import annotations

from dataclasses import dataclass

from app_core.application.apply_pull_payload import PullRepositories
from app_core.application.bootstrap_service import BootstrapService
from app_core.application.sync_pull_service import SyncPullService
from app_core.application.sync_push_service import SyncPushService
from app_core.application.sync_service import SyncService

from desktop.adapters.session_adapter import DesktopSessionAdapter
from desktop.adapters.http_adapter import DesktopHttpAdapter
from desktop.adapters.app_meta_repo_adapter import DesktopAppMetaRepoAdapter
from desktop.adapters.outbox_adapter import DesktopOutboxAdapter
from desktop.adapters.sync_state_adapter import DesktopSyncStateAdapter
from desktop.adapters.repositories.companies_repo_adapter import CompaniesRepoAdapter
from desktop.adapters.repositories.users_repo_adapter import UsersRepoAdapter
from desktop.adapters.repositories.devices_repo_adapter import DevicesRepoAdapter
from desktop.adapters.repositories.product_categories_repo_adapter import ProductCategoriesRepoAdapter
from desktop.adapters.repositories.products_repo_adapter import ProductsRepoAdapter
from desktop.adapters.repositories.product_barcodes_repo_adapter import ProductBarcodesRepoAdapter
from desktop.adapters.repositories.locations_repo_adapter import LocationsRepoAdapter
from desktop.adapters.repositories.zones_repo_adapter import ZonesRepoAdapter
from desktop.adapters.repositories.inventory_events_repo_adapter import InventoryEventsRepoAdapter
from desktop.adapters.repositories.inventory_event_targets_repo_adapter import InventoryEventTargetsRepoAdapter


@dataclass(frozen=True)
class AppCoreServices:
    bootstrap: BootstrapService
    sync_pull: SyncPullService
    sync_push: SyncPushService
    sync: SyncService


def build_services() -> AppCoreServices:
    session = DesktopSessionAdapter()
    http = DesktopHttpAdapter()
    app_meta = DesktopAppMetaRepoAdapter()

    pull_repos = PullRepositories(
        companies=CompaniesRepoAdapter(),
        users=UsersRepoAdapter(),
        devices=DevicesRepoAdapter(),
        product_categories=ProductCategoriesRepoAdapter(),
        products=ProductsRepoAdapter(),
        product_barcodes=ProductBarcodesRepoAdapter(),
        locations=LocationsRepoAdapter(),
        zones=ZonesRepoAdapter(),
        inventory_events=InventoryEventsRepoAdapter(),
        inventory_event_targets=InventoryEventTargetsRepoAdapter(),
    )

    sync_pull = SyncPullService(
        http=http,
        session=session,
        app_meta_repo=app_meta,
        repos=pull_repos,
    )
    sync_push = SyncPushService(
        http=http,
        session=session,
        outbox=DesktopOutboxAdapter(),
        sync_state=DesktopSyncStateAdapter(),
    )
    bootstrap = BootstrapService(
        session=session,
        app_meta_repo=app_meta,
        sync_pull_service=sync_pull,
    )
    sync = SyncService(
        session=session,
        app_meta_repo=app_meta,
        bootstrap_service=bootstrap,
        sync_pull_service=sync_pull,
        sync_push_service=sync_push,
    )

    return AppCoreServices(
        bootstrap=bootstrap,
        sync_pull=sync_pull,
        sync_push=sync_push,
        sync=sync,
    )
