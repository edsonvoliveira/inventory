# desktop/data/repositories/inventory_events_repo.py

"""
Responsibilities:
- Repository for inventory events data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig

_INVENTORY_EVENTS_CFG = RepoConfig(
    table="inventory_events_local",
    entity_name="inventory_events",

    uuid_col="uuid",

    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    active_col="is_active",
    source_col="source",

    enable_outbox=True,

    ui_writable_cols=(
        "location_server_id",
        "title",
        "event_type",
        "status",
        "required_counts",
        "required_audits",
        "tolerance_percent",
        "tolerance_absolute",
    ),

    server_upsert_cols=(
        "uuid",
        "server_id",
        "company_server_id",
        "location_server_id",
        "title",
        "event_type",
        "status",
        "required_counts",
        "required_audits",
        "tolerance_percent",
        "tolerance_absolute",
        "is_active",
        "created_at",
        "updated_at",
        "synced",
        "synced_at",
        "source",
    ),
)

class InventoryEventsRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_INVENTORY_EVENTS_CFG, conn)
