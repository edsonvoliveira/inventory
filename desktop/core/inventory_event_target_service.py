# desktop/core/inventory_event_target_service.py

"""
Responsibilities:
- Service layer for inventory event target workflows.
"""

from desktop.core.result import Result
from desktop.core.permissions import can_write_entity
from desktop.data.repositories.inventory_event_targets_repo import InventoryEventTargetsRepo
from desktop.utils.validation import parse_float


class InventoryEventTargetService:
    def list(self) -> Result[list[dict]]:
        try:
            data = InventoryEventTargetsRepo().get_all()
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar os targets.",
                error_code="TARGET_LIST_ERROR",
            )
        return Result(ok=True, data=data)

    def create(
        self,
        event_server_id: str | int | None,
        product_server_id: str | int | None,
        expected_qty: str | None,
    ) -> Result[None]:
        if not can_write_entity("inventory_event_targets"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        if not event_server_id or not product_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        qty = parse_float(expected_qty)
        try:
            InventoryEventTargetsRepo().create(
                {
                    "event_server_id": int(event_server_id),
                    "product_server_id": int(product_server_id),
                    "expected_qty": qty if qty is not None else 0,
                }
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar o target.",
                error_code="TARGET_CREATE_ERROR",
            )
        return Result(ok=True)

    def update(
        self,
        uuid: str,
        event_server_id: str | int | None,
        product_server_id: str | int | None,
        expected_qty: str | None,
    ) -> Result[None]:
        if not can_write_entity("inventory_event_targets"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        if not event_server_id or not product_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        qty = parse_float(expected_qty)
        try:
            InventoryEventTargetsRepo().update(
                uuid,
                {
                    "event_server_id": int(event_server_id),
                    "product_server_id": int(product_server_id),
                    "expected_qty": qty if qty is not None else 0,
                },
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar o target.",
                error_code="TARGET_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, uuid: str) -> Result[None]:
        if not can_write_entity("inventory_event_targets"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        try:
            InventoryEventTargetsRepo().soft_delete(uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover o target.",
                error_code="TARGET_DELETE_ERROR",
            )
        return Result(ok=True)
