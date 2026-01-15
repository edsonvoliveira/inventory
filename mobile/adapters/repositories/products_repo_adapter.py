from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.products_repo_port import ProductsRepoPort
from mobile.data.repositories.products_repo import upsert_many


class ProductsRepoAdapter(ProductsRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
