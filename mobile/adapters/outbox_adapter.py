from __future__ import annotations

from typing import Mapping, Any, Iterable, Sequence

from app_core.ports.outbox_port import OutboxPort
from mobile.data.repositories import outbox_repo


class MobileOutboxAdapter(OutboxPort):
    def enqueue(
        self,
        table_name: str,
        operation: str,
        record_uuid: str,
        payload: Mapping[str, Any],
    ) -> None:
        outbox_repo.add(table_name, operation, record_uuid, dict(payload))

    def list_pending(self, limit: int | None = None) -> Sequence[Mapping[str, Any]]:
        return outbox_repo.get_pending(limit or 100)

    def mark_done(self, outbox_ids: Iterable[int]) -> None:
        outbox_repo.mark_success(outbox_ids)

    def mark_failed(self, outbox_id: int, reason: str) -> None:
        outbox_repo.mark_failed(outbox_id, reason)
