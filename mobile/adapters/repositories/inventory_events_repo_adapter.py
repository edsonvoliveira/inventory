from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.inventory_events_repo_port import InventoryEventsRepoPort
from mobile.data.repositories.events_repo import upsert_many


class InventoryEventsRepoAdapter(InventoryEventsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
