# desktop/data/repositories/devices_repo.py

"""
Responsibilities:
- Repository for devices data.
- Define persistence and sync behavior.
"""

#desktop/data/repositories/devices_repo.py

"""
Responsabilities:
- Repository for devices entity
- Inherits basic CRUD, outbox, and sync from BaseRepo
- Configured via RepoConfig for devices-specific behavior
- Devices do not participate in sync push operations
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig

_DEVICES_CFG = RepoConfig(
    table="devices_local",
    entity_name="devices",

    uuid_col="uuid",

    # controle
    synced_col=None,          # devices não participam de push
    synced_at_col=None,
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    source_col="source",
    active_col=None,          # não existe is_active; há is_blocked

    enable_outbox=False,      # regra de domínio

    # UI NÃO cria device; apenas leitura
    ui_writable_cols=(),

    # pull / bootstrap
    server_upsert_cols=(
        "uuid",
        "server_id",
        "device_uuid",
        "device_name",
        "os",
        "app_version",
        "is_blocked",
        "created_at",
        "updated_at",
        "source",
    ),
)

class DevicesRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_DEVICES_CFG, conn)
