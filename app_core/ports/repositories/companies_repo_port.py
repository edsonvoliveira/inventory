from __future__ import annotations

from typing import Protocol, Mapping, Any, Iterable


class CompaniesRepoPort(Protocol):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        ...
