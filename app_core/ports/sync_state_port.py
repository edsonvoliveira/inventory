from __future__ import annotations

from typing import Protocol


class SyncStatePort(Protocol):
    def mark_record_synced(self, table_name: str, record_uuid: str, synced_at: str) -> None:
        ...
