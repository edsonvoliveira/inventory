# backend/app/services/sync/registry.py

# mapa table_name → handler

from typing import Dict
from app.services.sync.base import BaseSyncHandler
from app.services.sync.inventory_items import InventoryItemSyncHandler
from app.services.sync.products import ProductSyncHandler
from app.services.sync.product_categories import ProductCategorySyncHandler
from app.services.sync.locations import LocationSyncHandler
from app.services.sync.inventory_events import InventoryEventSyncHandler

SYNC_HANDLERS: Dict[str, BaseSyncHandler] = {
    "inventory_items": InventoryItemSyncHandler(),
    "products": ProductSyncHandler(),
    "product_categories": ProductCategorySyncHandler(),
    "locations": LocationSyncHandler(),
    "inventory_events": InventoryEventSyncHandler(),
}
