from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.companies_repo_port import CompaniesRepoPort
from mobile.data.repositories.companies_repo import upsert_many


class CompaniesRepoAdapter(CompaniesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
