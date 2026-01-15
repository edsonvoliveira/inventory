from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.companies_repo_port import CompaniesRepoPort
from desktop.data.repositories.companies_repo import CompaniesRepo


class CompaniesRepoAdapter(CompaniesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        CompaniesRepo().upsert_many(list(rows))
