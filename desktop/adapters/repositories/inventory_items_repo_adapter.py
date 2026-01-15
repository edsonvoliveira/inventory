from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.inventory_items_repo_port import InventoryItemsRepoPort
from desktop.data.repositories.inventory_items_repo import InventoryItemsRepo


class InventoryItemsRepoAdapter(InventoryItemsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        InventoryItemsRepo().upsert_many(list(rows))
