from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.locations_repo_port import LocationsRepoPort
from mobile.data.repositories.locations_repo import upsert_many


class LocationsRepoAdapter(LocationsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
