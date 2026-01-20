# desktop/data/repositories/zone_user_progress_repo.py

"""
Responsibilities:
- Repository for zone user progress data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig

_ZONE_USER_PROGRESS_CFG = RepoConfig(
    table="zone_user_progress_local",
    entity_name="zone_user_progress",

    uuid_col="uuid",

    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    source_col="source",

    active_col=None,
    enable_outbox=True,

    ui_writable_cols=(
        "zone_server_id",
        "user_server_id",
        "count_type",
        "started_at",
        "finished_at",
        "is_finished",
        "items_counted",
        "qty_total",
        "device_id",
    ),

    server_upsert_cols=(
        "uuid",
        "server_id",
        "zone_server_id",
        "user_server_id",
        "count_type",
        "started_at",
        "finished_at",
        "is_finished",
        "items_counted",
        "qty_total",
        "device_id",
        "synced",
        "synced_at",
        "source",
    ),
)

class ZoneUserProgressRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_ZONE_USER_PROGRESS_CFG, conn)

    def _zone_is_closed(self, zone_server_id: int | None) -> bool:
        if zone_server_id is None:
            return False
        row = self.conn.execute(
            """
            SELECT count_status, lock_status
            FROM zones_local
            WHERE server_id = ?
            """,
            (zone_server_id,),
        ).fetchone()
        if not row:
            return False
        count_status, lock_status = row
        return count_status in {"finished", "locked"} or lock_status == "locked"

    def update(self, uuid: str, data: dict):
        record = self.get_by_uuid(uuid)
        zone_server_id = record.get("zone_server_id") if record else None
        if self._zone_is_closed(zone_server_id):
            raise RuntimeError("zone_user_progress append-only: zona fechada")
        return super().update(uuid, data)

    def soft_delete(self, uuid: str):
        raise RuntimeError("zone_user_progress append-only: delete nao permitido")

    def restore(self, uuid: str):
        raise RuntimeError("zone_user_progress append-only: restore nao permitido")
