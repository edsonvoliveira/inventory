# desktop/core/inventory_event_service.py

"""
Responsibilities:
- Service layer for inventory event workflows.
"""

from desktop.core.result import Result
from desktop.core.permissions import can_write_entity
from desktop.data.db.connection import get_connection
from desktop.data.repositories.inventory_events_repo import InventoryEventsRepo
from desktop.utils.validation import is_required, parse_float


class InventoryEventService:
    def _event_metadata(self, uuid: str) -> tuple[int | None, int | None]:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT server_id, required_counts
                FROM inventory_events_local
                WHERE uuid = ?
                """,
                (uuid,),
            ).fetchone()
            if not row:
                return None, None
            server_id, required_counts = row
            return (
                int(server_id) if server_id is not None else None,
                int(required_counts) if required_counts is not None else None,
            )
        finally:
            conn.close()

    def _current_status(self, uuid: str) -> str | None:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT status FROM inventory_events_local WHERE uuid = ?",
                (uuid,),
            ).fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def _zones_for_event(self, event_server_id: int) -> list[int]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT server_id
                FROM zones_local
                WHERE event_server_id = ?
                """,
                (event_server_id,),
            ).fetchall()
            return [int(r[0]) for r in rows if r and r[0] is not None]
        finally:
            conn.close()

    def _finished_primary_counts(self, zone_server_id: int) -> int:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT COUNT(1)
                FROM zone_user_progress_local
                WHERE zone_server_id = ?
                  AND is_finished = 1
                  AND count_type = 'primary'
                """,
                (zone_server_id,),
            ).fetchone()
            return int(row[0] or 0) if row else 0
        finally:
            conn.close()
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
        if not can_write_entity("inventory_events"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
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
        if not can_write_entity("inventory_events"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        if not is_required(title) or not is_required(status) or not location_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        current_status = self._current_status(uuid)
        if (current_status or "").lower() in {"closed", "finalized"}:
            return Result(
                ok=False,
                message="Evento fechado nao permite edicao.",
                error_code="EVENT_READ_ONLY",
            )
        normalized_status = (status or "").strip().lower()
        if normalized_status in {"closed", "finalized"}:
            event_server_id, stored_required_counts = self._event_metadata(uuid)
            parsed_required_counts = int(required_counts) if str(required_counts or "").isdigit() else None
            effective_required_counts = parsed_required_counts if parsed_required_counts is not None else stored_required_counts
            if effective_required_counts and effective_required_counts > 0:
                if event_server_id is None:
                    return Result(
                        ok=False,
                        message="Evento sem identificador no servidor.",
                        error_code="EVENT_SERVER_ID_MISSING",
                    )
                for zone_server_id in self._zones_for_event(event_server_id):
                    finished_counts = self._finished_primary_counts(zone_server_id)
                    if finished_counts < effective_required_counts:
                        return Result(
                            ok=False,
                            message="Required counts nao atingido para fechar o evento.",
                            error_code="REQUIRED_COUNTS_NOT_MET",
                        )
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
        if not can_write_entity("inventory_events"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        try:
            InventoryEventsRepo().soft_delete(uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover o evento.",
                error_code="EVENT_DELETE_ERROR",
            )
        return Result(ok=True)
