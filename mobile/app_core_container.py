from __future__ import annotations

from dataclasses import dataclass

from app_core.application.apply_pull_payload import PullRepositories
from app_core.application.bootstrap_service import BootstrapService
from app_core.application.sync_pull_service import SyncPullService
from app_core.application.sync_push_service import SyncPushService
from app_core.application.sync_service import SyncService

from mobile.adapters.session_adapter import MobileSessionAdapter
from mobile.adapters.http_adapter import MobileHttpAdapter
from mobile.adapters.app_meta_repo_adapter import MobileAppMetaRepoAdapter
from mobile.adapters.outbox_adapter import MobileOutboxAdapter
from mobile.adapters.sync_state_adapter import MobileSyncStateAdapter
from mobile.adapters.repositories.companies_repo_adapter import CompaniesRepoAdapter
from mobile.adapters.repositories.users_repo_adapter import UsersRepoAdapter
from mobile.adapters.repositories.devices_repo_adapter import DevicesRepoAdapter
from mobile.adapters.repositories.product_categories_repo_adapter import ProductCategoriesRepoAdapter
from mobile.adapters.repositories.products_repo_adapter import ProductsRepoAdapter
from mobile.adapters.repositories.product_barcodes_repo_adapter import ProductBarcodesRepoAdapter
from mobile.adapters.repositories.locations_repo_adapter import LocationsRepoAdapter
from mobile.adapters.repositories.zones_repo_adapter import ZonesRepoAdapter
from mobile.adapters.repositories.inventory_events_repo_adapter import InventoryEventsRepoAdapter
from mobile.adapters.repositories.inventory_event_targets_repo_adapter import InventoryEventTargetsRepoAdapter
from mobile.adapters.repositories.inventory_items_repo_adapter import InventoryItemsRepoAdapter
from mobile.adapters.repositories.zone_user_progress_repo_adapter import ZoneUserProgressRepoAdapter


@dataclass(frozen=True)
class AppCoreServices:
    bootstrap: BootstrapService
    sync_pull: SyncPullService
    sync_push: SyncPushService
    sync: SyncService


def build_services() -> AppCoreServices:
    session = MobileSessionAdapter()
    http = MobileHttpAdapter()
    app_meta = MobileAppMetaRepoAdapter()

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
        inventory_items=InventoryItemsRepoAdapter(),
        zone_user_progress=ZoneUserProgressRepoAdapter(),
    )

    sync_pull = SyncPullService(
        http=http,
        session=session,
        app_meta_repo=app_meta,
        repos=pull_repos,
        sync_state=MobileSyncStateAdapter(),
    )
    sync_push = SyncPushService(
        http=http,
        session=session,
        outbox=MobileOutboxAdapter(),
        sync_state=MobileSyncStateAdapter(),
        endpoint="/v1/sync/mobile/push",
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
