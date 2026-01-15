from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.product_categories_repo_port import ProductCategoriesRepoPort
from desktop.data.repositories.product_categories_repo import ProductCategoriesRepo


class ProductCategoriesRepoAdapter(ProductCategoriesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        ProductCategoriesRepo().upsert_many(list(rows))
