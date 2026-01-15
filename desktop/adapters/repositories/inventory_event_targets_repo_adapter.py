from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.inventory_event_targets_repo_port import InventoryEventTargetsRepoPort
from desktop.data.repositories.inventory_event_targets_repo import InventoryEventTargetsRepo


class InventoryEventTargetsRepoAdapter(InventoryEventTargetsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        InventoryEventTargetsRepo().upsert_many(list(rows))
