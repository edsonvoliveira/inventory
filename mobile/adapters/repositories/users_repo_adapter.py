from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.users_repo_port import UsersRepoPort
from mobile.data.repositories.users_repo import upsert_many


class UsersRepoAdapter(UsersRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
