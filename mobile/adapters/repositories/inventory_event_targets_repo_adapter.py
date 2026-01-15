from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.inventory_event_targets_repo_port import InventoryEventTargetsRepoPort
from mobile.data.repositories.event_targets_repo import upsert_many


class InventoryEventTargetsRepoAdapter(InventoryEventTargetsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
