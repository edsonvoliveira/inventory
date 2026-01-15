from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.devices_repo_port import DevicesRepoPort
from mobile.data.repositories.devices_repo import upsert_many


class DevicesRepoAdapter(DevicesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
