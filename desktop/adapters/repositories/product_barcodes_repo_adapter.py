from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.product_barcodes_repo_port import ProductBarcodesRepoPort
from desktop.data.repositories.product_barcodes_repo import ProductBarcodesRepo


class ProductBarcodesRepoAdapter(ProductBarcodesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        ProductBarcodesRepo().upsert_many(list(rows))
