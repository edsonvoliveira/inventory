from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.users_repo_port import UsersRepoPort
from desktop.data.repositories.users_repo import UsersRepo


class UsersRepoAdapter(UsersRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        UsersRepo().upsert_many(list(rows))
