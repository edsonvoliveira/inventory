# desktop/data/repositories/inventory_items_repo.py

"""
Responsabilities:
- Repository for inventory_items entity
- Inherits basic CRUD, outbox, and sync from BaseRepo
- Configured via RepoConfig for inventory_items-specific behavior
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig


_INVENTORY_ITEMS_CFG = RepoConfig(
    table="inventory_items_local",
    entity_name="inventory_items",

    uuid_col="uuid",

    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    source_col="source",

    # itens operacionais NÃO têm is_active
    active_col=None,

    enable_outbox=True,

    ui_writable_cols=(
        "zone_server_id",
        "product_server_id",
        "user_server_id",
        "scanned_code",
        "qty_counted",
        "batch_number",
        "expiry_date",
        "is_new_product",
        "device_timestamp",
        "device_id",
        "latitude",
        "longitude",
    ),

    server_upsert_cols=(
        "uuid",
        "server_id",
        "zone_server_id",
        "product_server_id",
        "user_server_id",
        "scanned_code",
        "qty_counted",
        "batch_number",
        "expiry_date",
        "is_new_product",
        "device_timestamp",
        "server_timestamp",
        "device_id",
        "latitude",
        "longitude",
        "deleted_at",
        "synced",
        "synced_at",
        "source",
    ),
)


class InventoryItemsRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_INVENTORY_ITEMS_CFG, conn)