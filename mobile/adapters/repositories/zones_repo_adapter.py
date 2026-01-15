from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.zones_repo_port import ZonesRepoPort
from mobile.data.repositories.zones_repo import upsert_many


class ZonesRepoAdapter(ZonesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
