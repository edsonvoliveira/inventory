# desktop/core/zones_service.py

"""
Responsibilities:
- Service layer for zones workflows.
"""

from desktop.core.result import Result
from desktop.data.repositories.zones_repo import ZonesRepo
from desktop.utils.validation import is_required


class ZonesService:
    def list(self) -> Result[list[dict]]:
        try:
            data = ZonesRepo().get_all()
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar as zonas.",
                error_code="ZONE_LIST_ERROR",
            )
        return Result(ok=True, data=data)

    def create(
        self,
        event_server_id: str | int | None,
        name: str,
        description: str | None,
        count_status: str | None,
        lock_status: str | None,
    ) -> Result[None]:
        if not is_required(name) or not event_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        try:
            ZonesRepo().create(
                {
                    "event_server_id": int(event_server_id),
                    "name": name.strip(),
                    "description": (description or "").strip() or None,
                    "count_status": (count_status or "").strip() or None,
                    "lock_status": (lock_status or "").strip() or None,
                }
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar a zona.",
                error_code="ZONE_CREATE_ERROR",
            )
        return Result(ok=True)

    def update(
        self,
        uuid: str,
        event_server_id: str | int | None,
        name: str,
        description: str | None,
        count_status: str | None,
        lock_status: str | None,
    ) -> Result[None]:
        if not is_required(name) or not event_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        try:
            ZonesRepo().update(
                uuid,
                {
                    "event_server_id": int(event_server_id),
                    "name": name.strip(),
                    "description": (description or "").strip() or None,
                    "count_status": (count_status or "").strip() or None,
                    "lock_status": (lock_status or "").strip() or None,
                },
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar a zona.",
                error_code="ZONE_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, uuid: str) -> Result[None]:
        try:
            ZonesRepo().soft_delete(uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover a zona.",
                error_code="ZONE_DELETE_ERROR",
            )
        return Result(ok=True)
