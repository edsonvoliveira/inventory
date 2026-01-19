# desktop/core/inventory_event_service.py

"""
Responsibilities:
- Service layer for inventory event workflows.
"""

from desktop.core.result import Result
from desktop.data.repositories.inventory_events_repo import InventoryEventsRepo
from desktop.utils.validation import is_required, parse_float


class InventoryEventService:
    def list(self) -> Result[list[dict]]:
        try:
            data = InventoryEventsRepo().get_all()
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar os eventos.",
                error_code="EVENT_LIST_ERROR",
            )
        return Result(ok=True, data=data)

    def create(
        self,
        location_server_id: str | int | None,
        title: str,
        event_type: str | None,
        status: str,
        required_counts: str | None,
        required_audits: str | None,
        tolerance_percent: str | None,
        tolerance_absolute: str | None,
    ) -> Result[None]:
        if not is_required(title) or not is_required(status) or not location_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        data = {
            "location_server_id": int(location_server_id),
            "title": title.strip(),
            "event_type": (event_type or "").strip() or None,
            "status": status.strip(),
            "required_counts": int(required_counts) if str(required_counts or "").isdigit() else None,
            "required_audits": int(required_audits) if str(required_audits or "").isdigit() else None,
            "tolerance_percent": parse_float(tolerance_percent),
            "tolerance_absolute": parse_float(tolerance_absolute),
        }
        try:
            InventoryEventsRepo().create(data)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar o evento.",
                error_code="EVENT_CREATE_ERROR",
            )
        return Result(ok=True)

    def update(
        self,
        uuid: str,
        location_server_id: str | int | None,
        title: str,
        event_type: str | None,
        status: str,
        required_counts: str | None,
        required_audits: str | None,
        tolerance_percent: str | None,
        tolerance_absolute: str | None,
    ) -> Result[None]:
        if not is_required(title) or not is_required(status) or not location_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        data = {
            "location_server_id": int(location_server_id),
            "title": title.strip(),
            "event_type": (event_type or "").strip() or None,
            "status": status.strip(),
            "required_counts": int(required_counts) if str(required_counts or "").isdigit() else None,
            "required_audits": int(required_audits) if str(required_audits or "").isdigit() else None,
            "tolerance_percent": parse_float(tolerance_percent),
            "tolerance_absolute": parse_float(tolerance_absolute),
        }
        try:
            InventoryEventsRepo().update(uuid, data)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar o evento.",
                error_code="EVENT_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, uuid: str) -> Result[None]:
        try:
            InventoryEventsRepo().soft_delete(uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover o evento.",
                error_code="EVENT_DELETE_ERROR",
            )
        return Result(ok=True)
