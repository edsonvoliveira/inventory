# desktop/core/product_service.py

"""
Responsibilities:
- Service layer for product workflows.
"""

from __future__ import annotations

from datetime import datetime

from desktop.core.result import Result
from desktop.core.permissions import can_write_entity
from desktop.core.strings import ERROR_INVALID_PRICE
from desktop.data.repositories.product_barcodes_repo import ProductBarcodesRepo
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.data.repository import (
    company_get_all,
    product_barcode_get_uuids_by_product_server_id,
    product_get_all,
    product_get_uuid_and_server_id,
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
        if not can_write_entity("products"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
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
            ProductsRepo().create(
                {
                    "sku": sku.strip(),
                    "name": name.strip(),
                    "uom_base": unit,
                    "uom_inventory": unit,
                    "cost_price": unit_cost,
                    "description": None,
                }
            )
            # Barcode is created only when product has server_id (synced).
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
        if not can_write_entity("products"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
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
            product_uuid, product_server_id = product_get_uuid_and_server_id(product_id)
            if not product_uuid:
                return Result(ok=False, message="Produto nao encontrado.", error_code="PRODUCT_NOT_FOUND")
            ProductsRepo().update(
                product_uuid,
                {
                    "sku": sku.strip(),
                    "name": name.strip(),
                    "uom_base": unit,
                    "uom_inventory": unit,
                    "cost_price": unit_cost,
                },
            )
            if barcode and product_server_id is not None:
                ProductBarcodesRepo().create(
                    {
                        "product_server_id": int(product_server_id),
                        "barcode": barcode.strip(),
                        "description": None,
                    }
                )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar o produto.",
                error_code="PRODUCT_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, product_id: int) -> Result[None]:
        if not can_write_entity("products"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        try:
            product_uuid, product_server_id = product_get_uuid_and_server_id(product_id)
            if not product_uuid:
                return Result(
                    ok=False,
                    message="Produto nao encontrado.",
                    error_code="PRODUCT_NOT_FOUND",
                )
            ProductsRepo().soft_delete(product_uuid)
            if product_server_id is not None:
                for barcode_uuid in product_barcode_get_uuids_by_product_server_id(product_server_id):
                    ProductBarcodesRepo().soft_delete(barcode_uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover o produto.",
                error_code="PRODUCT_DELETE_ERROR",
            )
        return Result(ok=True)
