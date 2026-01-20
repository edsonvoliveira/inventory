# desktop/core/product_barcode_service.py

"""
Responsibilities:
- Service layer for product barcode workflows.
"""

from desktop.core.result import Result
from desktop.core.permissions import can_write_entity
from desktop.data.repositories.product_barcodes_repo import ProductBarcodesRepo
from desktop.utils.validation import is_required


class ProductBarcodeService:
    def list(self) -> Result[list[dict]]:
        try:
            data = ProductBarcodesRepo().get_all()
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar os codigos.",
                error_code="BARCODE_LIST_ERROR",
            )
        return Result(ok=True, data=data)

    def create(self, product_server_id: str | int | None, barcode: str, description: str | None) -> Result[None]:
        if not can_write_entity("product_barcodes"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        if not is_required(barcode) or not product_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        try:
            ProductBarcodesRepo().create(
                {
                    "product_server_id": int(product_server_id),
                    "barcode": barcode.strip(),
                    "description": (description or "").strip() or None,
                }
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar o codigo.",
                error_code="BARCODE_CREATE_ERROR",
            )
        return Result(ok=True)

    def update(
        self,
        uuid: str,
        product_server_id: str | int | None,
        barcode: str,
        description: str | None,
    ) -> Result[None]:
        if not can_write_entity("product_barcodes"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        if not is_required(barcode) or not product_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        try:
            ProductBarcodesRepo().update(
                uuid,
                {
                    "product_server_id": int(product_server_id),
                    "barcode": barcode.strip(),
                    "description": (description or "").strip() or None,
                },
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar o codigo.",
                error_code="BARCODE_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, uuid: str) -> Result[None]:
        if not can_write_entity("product_barcodes"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        try:
            ProductBarcodesRepo().soft_delete(uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover o codigo.",
                error_code="BARCODE_DELETE_ERROR",
            )
        return Result(ok=True)
