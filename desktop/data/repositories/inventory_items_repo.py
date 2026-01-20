# desktop/data/repositories/inventory_items_repo.py

"""
Responsibilities:
- Repository for inventory items data.
- Define persistence and sync behavior.
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
        "synced",
        "synced_at",
        "source",
    ),
)


class InventoryItemsRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_INVENTORY_ITEMS_CFG, conn)

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
            raise RuntimeError("inventory_items append-only: zona fechada")
        return super().update(uuid, data)

    def soft_delete(self, uuid: str):
        raise RuntimeError("inventory_items append-only: delete nao permitido")

    def restore(self, uuid: str):
        raise RuntimeError("inventory_items append-only: restore nao permitido")
