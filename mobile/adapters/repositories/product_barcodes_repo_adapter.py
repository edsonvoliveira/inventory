from __future__ import annotations

from typing import Mapping, Any, Iterable

from app_core.ports.repositories.product_barcodes_repo_port import ProductBarcodesRepoPort
from mobile.data.repositories.product_barcodes_repo import upsert_many


class ProductBarcodesRepoAdapter(ProductBarcodesRepoPort):
    def upsert_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        upsert_many(list(rows))
