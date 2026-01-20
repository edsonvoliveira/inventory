# desktop/core/zones_service.py

"""
Responsibilities:
- Service layer for zones workflows.
"""

from desktop.core.result import Result
from desktop.core.permissions import can_write_entity
from desktop.data.db.connection import get_connection
from desktop.data.repositories.zones_repo import ZonesRepo
from desktop.utils.validation import is_required


class ZonesService:
    def _required_counts(self, event_server_id: int) -> int | None:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT required_counts
                FROM inventory_events_local
                WHERE server_id = ?
                """,
                (event_server_id,),
            ).fetchone()
            if not row:
                return None
            value = row[0]
            return int(value) if value is not None else None
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

    def _zone_server_id(self, uuid: str) -> int | None:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT server_id
                FROM zones_local
                WHERE uuid = ?
                """,
                (uuid,),
            ).fetchone()
            return int(row[0]) if row and row[0] is not None else None
        finally:
            conn.close()

    def _zone_state(self, uuid: str) -> tuple[str | None, str | None, int | None]:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT count_status, lock_status, event_server_id
                FROM zones_local
                WHERE uuid = ?
                """,
                (uuid,),
            ).fetchone()
            if not row:
                return None, None, None
            count_status, lock_status, event_server_id = row
            return count_status, lock_status, event_server_id
        finally:
            conn.close()

    def _event_status(self, event_server_id: int | None) -> str | None:
        if event_server_id is None:
            return None
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT status
                FROM inventory_events_local
                WHERE server_id = ?
                """,
                (event_server_id,),
            ).fetchone()
            return row[0] if row else None
        finally:
            conn.close()

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
        if not can_write_entity("zones"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
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
        if not can_write_entity("zones"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        if not is_required(name) or not event_server_id:
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        current_count_status, current_lock_status, current_event_server_id = self._zone_state(uuid)
        if (current_count_status or "").lower() in {"finished", "locked"} or (current_lock_status or "").lower() == "locked":
            return Result(ok=False, message="Zona fechada nao permite edicao.", error_code="ZONE_READ_ONLY")
        event_status = self._event_status(current_event_server_id)
        if (event_status or "").lower() in {"closed", "finalized"}:
            return Result(ok=False, message="Evento fechado nao permite edicao.", error_code="ZONE_READ_ONLY")
        normalized_status = (count_status or "").strip().lower()
        if normalized_status == "finished":
            required_counts = self._required_counts(int(event_server_id))
            if required_counts and required_counts > 0:
                zone_server_id = self._zone_server_id(uuid)
                if zone_server_id is None:
                    return Result(
                        ok=False,
                        message="Zona sem identificador no servidor.",
                        error_code="ZONE_SERVER_ID_MISSING",
                    )
                finished_counts = self._finished_primary_counts(zone_server_id)
                if finished_counts < required_counts:
                    return Result(
                        ok=False,
                        message="Required counts nao atingido para fechar a zona.",
                        error_code="REQUIRED_COUNTS_NOT_MET",
                    )
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
        if not can_write_entity("zones"):
            return Result(ok=False, message="Operacao nao permitida.", error_code="OPERATION_NOT_ALLOWED_FOR_ORIGIN")
        current_count_status, current_lock_status, current_event_server_id = self._zone_state(uuid)
        if (current_count_status or "").lower() in {"finished", "locked"} or (current_lock_status or "").lower() == "locked":
            return Result(ok=False, message="Zona fechada nao permite edicao.", error_code="ZONE_READ_ONLY")
        event_status = self._event_status(current_event_server_id)
        if (event_status or "").lower() in {"closed", "finalized"}:
            return Result(ok=False, message="Evento fechado nao permite edicao.", error_code="ZONE_READ_ONLY")
        try:
            ZonesRepo().soft_delete(uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover a zona.",
                error_code="ZONE_DELETE_ERROR",
            )
        return Result(ok=True)
