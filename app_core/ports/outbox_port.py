from __future__ import annotations

from typing import Protocol, Mapping, Any, Iterable, Sequence


class OutboxPort(Protocol):
    def enqueue(
        self,
        table_name: str,
        operation: str,
        record_uuid: str,
        payload: Mapping[str, Any],
    ) -> None:
        ...

    def list_pending(self, limit: int | None = None) -> Sequence[Mapping[str, Any]]:
        ...

    def mark_done(self, outbox_ids: Iterable[int]) -> None:
        ...

    def mark_failed(self, outbox_id: int, reason: str) -> None:
        ...
