from __future__ import annotations

from app_core.ports.sync_state_port import SyncStatePort
from mobile.data.db.connection import get_connection


class MobileSyncStateAdapter(SyncStatePort):
    def mark_record_synced(self, table_name: str, record_uuid: str, synced_at: str) -> None:
        conn = get_connection()
        try:
            conn.execute(
                f"UPDATE {table_name}_local SET synced = 1, synced_at = ? WHERE uuid = ?",
                (synced_at, record_uuid),
            )
            conn.commit()
        finally:
            conn.close()

    def set_record_server_id(self, table_name: str, record_uuid: str, server_id: int) -> None:
        conn = get_connection()
        try:
            conn.execute(
                f"UPDATE {table_name}_local SET server_id = ? WHERE uuid = ?",
                (server_id, record_uuid),
            )
            conn.commit()
        finally:
            conn.close()

    def set_last_server_sync_at(self, value: str, company_id: int | None = None) -> None:
        key = "last_server_sync_at" if company_id is None else f"last_server_sync_at:{company_id}"
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO app_meta (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
            conn.commit()
        finally:
            conn.close()
