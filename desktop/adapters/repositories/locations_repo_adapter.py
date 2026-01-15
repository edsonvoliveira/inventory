from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.locations_repo_port import LocationsRepoPort
from desktop.data.repositories.locations_repo import LocationsRepo


class LocationsRepoAdapter(LocationsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        LocationsRepo().upsert_many(list(rows))
