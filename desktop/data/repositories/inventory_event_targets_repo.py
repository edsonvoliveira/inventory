# desktop/data/repositories/inventory_event_targets_repo.py

"""
Responsibilities:
- Repository for inventory event targets data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig


_INVENTORY_EVENT_TARGETS_CFG = RepoConfig(
    table="inventory_event_targets_local",
    entity_name="inventory_event_targets",

    uuid_col="uuid",

    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    active_col="is_active",
    source_col="source",

    enable_outbox=True,

    ui_writable_cols=(
        "event_server_id",
        "product_server_id",
        "expected_qty",
    ),

    server_upsert_cols=(
        "uuid",
        "server_id",
        "company_server_id",
        "event_server_id",
        "product_server_id",
        "expected_qty",
        "is_active",
        "created_at",
        "updated_at",
        "synced",
        "synced_at",
        "source",
    ),
)


class InventoryEventTargetsRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_INVENTORY_EVENT_TARGETS_CFG, conn)
