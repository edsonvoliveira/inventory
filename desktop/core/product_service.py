# desktop/core/product_service.py

"""
Responsibilities:
- Service layer for product workflows.
"""

from __future__ import annotations

from datetime import datetime

from desktop.core.result import Result
from desktop.core.strings import ERROR_INVALID_PRICE
from desktop.core.session_service import SessionService
from desktop.data.repository import (
    company_get_all,
    company_get_local_id_by_server_id,
    product_create,
    product_delete,
    product_get_all,
    product_update,
)
from desktop.utils.validation import is_required, parse_float


class ProductService:
    def _resolve_company_id(self) -> int | None:
        companies = company_get_all()
        if not companies:
            return None
        return int(companies[0]["id"])

    def list(self) -> Result[list[dict]]:
        try:
            return Result(ok=True, data=product_get_all())
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar os produtos.",
                error_code="PRODUCT_LIST_ERROR",
            )

    def create(
        self,
        sku: str,
        barcode: str,
        name: str,
        unit_cost_raw: str,
        unit_of_measure: str,
    ) -> Result[None]:
        if not is_required(sku) or not is_required(name):
            return Result(ok=False, message="Campos obrigatorios.", error_code="VALIDATION_ERROR")
        unit_cost = parse_float(unit_cost_raw)
        if unit_cost is None:
            return Result(ok=False, message=ERROR_INVALID_PRICE, error_code="INVALID_PRICE")
        company_id = self._resolve_company_id()
        if not company_id:
            return Result(
                ok=False,
                message="Empresa nao encontrada para o usuario.",
                error_code="COMPANY_REQUIRED",
            )
        unit = unit_of_measure.strip() if unit_of_measure and unit_of_measure.strip() else "UN"
        try:
            product_create(
                sku.strip(),
                barcode,
                name.strip(),
                unit_cost,
                unit,
                datetime.now().isoformat(),
                company_id,
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar o produto.",
                error_code="PRODUCT_CREATE_ERROR",
            )
        return Result(ok=True)

    def update(
        self,
        product_id: int,
        sku: str,
        barcode: str,
        name: str,
        unit_cost_raw: str,
        unit_of_measure: str,
    ) -> Result[None]:
        if not is_required(sku) or not is_required(name):
            return Result(ok=False, message="Campos obrigatorios.", error_code="VALIDATION_ERROR")
        unit_cost = parse_float(unit_cost_raw)
        if unit_cost is None:
            return Result(ok=False, message=ERROR_INVALID_PRICE, error_code="INVALID_PRICE")
        company_id = self._resolve_company_id()
        if not company_id:
            return Result(
                ok=False,
                message="Empresa nao encontrada para o usuario.",
                error_code="COMPANY_REQUIRED",
            )
        unit = unit_of_measure.strip() if unit_of_measure and unit_of_measure.strip() else "UN"
        try:
            product_update(
                product_id,
                sku.strip(),
                barcode,
                name.strip(),
                unit_cost,
                unit,
                datetime.now().isoformat(),
                company_id,
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar o produto.",
                error_code="PRODUCT_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, product_id: int) -> Result[None]:
        try:
            product_delete(product_id)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover o produto.",
                error_code="PRODUCT_DELETE_ERROR",
            )
        return Result(ok=True)
