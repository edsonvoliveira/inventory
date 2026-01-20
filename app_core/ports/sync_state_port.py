from __future__ import annotations

from typing import Protocol


class SyncStatePort(Protocol):
    def mark_record_synced(self, table_name: str, record_uuid: str, synced_at: str) -> None:
        ...

    def set_record_server_id(self, table_name: str, record_uuid: str, server_id: int) -> None:
        ...

    def set_last_server_sync_at(self, value: str, company_id: int | None = None) -> None:
        ...
