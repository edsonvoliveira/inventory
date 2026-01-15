# backend/app/services/sync/registry.py

"""
Responsibilities:
- Sync service component for registry.
- Coordinate sync workflow steps.
"""

# backend/app/services/sync/registry.py

# mapa table_name → handler

from typing import Dict
from app.services.sync.handlers.base import BaseSyncHandler
from app.services.sync.handlers.companies import CompanySyncHandler
from app.services.sync.handlers.inventory_items import InventoryItemSyncHandler
from app.services.sync.handlers.products import ProductSyncHandler
from app.services.sync.handlers.product_categories import ProductCategorySyncHandler
from app.services.sync.handlers.locations import LocationSyncHandler
from app.services.sync.handlers.inventory_events import InventoryEventSyncHandler
from app.services.sync.handlers.inventory_event_targets import InventoryEventTargetSyncHandler
from app.services.sync.handlers.product_barcodes import ProductBarcodeSyncHandler
from app.services.sync.handlers.zones import ZoneSyncHandler
from app.services.sync.handlers.devices import DeviceSyncHandler
from app.services.sync.handlers.users import UserSyncHandler
from app.services.sync.handlers.zone_user_progress import ZoneUserProgressHandler

SYNC_HANDLERS: Dict[str, BaseSyncHandler] = {
    "companies": CompanySyncHandler(),
    "inventory_items": InventoryItemSyncHandler(),
    "products": ProductSyncHandler(),
    "product_categories": ProductCategorySyncHandler(),
    "locations": LocationSyncHandler(),
    "inventory_events": InventoryEventSyncHandler(),
    "inventory_event_targets": InventoryEventTargetSyncHandler(),
    "product_barcodes": ProductBarcodeSyncHandler(),
    "zones": ZoneSyncHandler(),
    "devices": DeviceSyncHandler(),
    "users": UserSyncHandler(),
    "zone_user_progress": ZoneUserProgressHandler(),
}
