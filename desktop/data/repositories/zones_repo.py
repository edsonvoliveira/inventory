# desktop/data/repositories/zones_repo.py

"""
Responsabilities:
- Repository for zones entity
- Inherits basic CRUD, outbox, and sync from BaseRepo
- Configured via RepoConfig for zones-specific behavior
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig


_ZONES_CFG = RepoConfig(
    table="zones_local",
    entity_name="zones",

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
        "name",
        "description",
        "count_status",
        "lock_status",
    ),

    server_upsert_cols=(
        "uuid",
        "server_id",
        "event_server_id",
        "name",
        "description",
        "count_status",
        "lock_status",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
        "synced",
        "synced_at",
        "source",
    ),
)


class ZonesRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_ZONES_CFG, conn)