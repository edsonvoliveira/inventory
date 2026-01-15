from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.product_categories_repo_port import ProductCategoriesRepoPort
from mobile.data.repositories.product_categories_repo import upsert_many


class ProductCategoriesRepoAdapter(ProductCategoriesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
