from __future__ import annotations

from app_core.ports.sync_state_port import SyncStatePort
from desktop.data.db.connection import get_connection


class DesktopSyncStateAdapter(SyncStatePort):
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
