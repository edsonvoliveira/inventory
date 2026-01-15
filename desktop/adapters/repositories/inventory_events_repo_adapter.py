from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.inventory_events_repo_port import InventoryEventsRepoPort
from desktop.data.repositories.inventory_events_repo import InventoryEventsRepo


class InventoryEventsRepoAdapter(InventoryEventsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        InventoryEventsRepo().upsert_many(list(rows))
