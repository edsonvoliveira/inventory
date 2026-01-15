from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.devices_repo_port import DevicesRepoPort
from desktop.data.repositories.devices_repo import DevicesRepo


class DevicesRepoAdapter(DevicesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        DevicesRepo().upsert_many(list(rows))
