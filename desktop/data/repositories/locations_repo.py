# desktop/data/repositories/locations_repo.py

"""
Responsibilities:
- Repository for locations data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig

_LOCATIONS_CFG = RepoConfig(
    table="locations_local",
    entity_name="locations",

    uuid_col="uuid",

    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    active_col="is_active",
    source_col="source",

    enable_outbox=True,

    ui_writable_cols=(
        "code",
        "name",
        "address",
    ),

    server_upsert_cols=(
        "uuid",
        "server_id",
        "company_server_id",
        "code",
        "name",
        "address",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
        "synced",
        "synced_at",
        "source",
    ),
)

class LocationsRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_LOCATIONS_CFG, conn)
