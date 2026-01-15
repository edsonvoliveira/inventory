from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.zone_user_progress_repo_port import ZoneUserProgressRepoPort
from desktop.data.repositories.zone_user_progress_repo import ZoneUserProgressRepo


class ZoneUserProgressRepoAdapter(ZoneUserProgressRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        ZoneUserProgressRepo().upsert_many(list(rows))
