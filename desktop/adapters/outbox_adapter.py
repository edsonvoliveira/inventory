from __future__ import annotations

from typing import Mapping, Any, Iterable, Sequence

from app_core.ports.outbox_port import OutboxPort
from desktop.data.db.connection import get_connection
from desktop.data.repositories.outbox_repo import OutboxRepo


class DesktopOutboxAdapter(OutboxPort):
    def enqueue(
        self,
        table_name: str,
        operation: str,
        record_uuid: str,
        payload: Mapping[str, Any],
    ) -> None:
        conn = get_connection()
        try:
            OutboxRepo(conn).add(table_name, operation, record_uuid, dict(payload))
            conn.commit()
        finally:
            conn.close()

    def list_pending(self, limit: int | None = None) -> Sequence[Mapping[str, Any]]:
        conn = get_connection()
        try:
            return OutboxRepo(conn).get_pending(limit or 100)
        finally:
            conn.close()

    def mark_done(self, outbox_ids: Iterable[int]) -> None:
        conn = get_connection()
        try:
            OutboxRepo(conn).mark_success(outbox_ids)
            conn.commit()
        finally:
            conn.close()

    def mark_failed(self, outbox_id: int, reason: str) -> None:
        conn = get_connection()
        try:
            OutboxRepo(conn).mark_failed(outbox_id, reason)
            conn.commit()
        finally:
            conn.close()
