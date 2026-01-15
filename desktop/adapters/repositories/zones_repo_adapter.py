from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.zones_repo_port import ZonesRepoPort
from desktop.data.repositories.zones_repo import ZonesRepo


class ZonesRepoAdapter(ZonesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        ZonesRepo().upsert_many(list(rows))
