from __future__ import annotations

from datetime import datetime, timezone

from app_core.ports.http_port import HttpPort
from app_core.ports.session_port import SessionPort
from app_core.ports.outbox_port import OutboxPort
from app_core.ports.sync_state_port import SyncStatePort

SYNC_PUSH_ENDPOINT = "/v1/sync/push"


class SyncPushService:
    def __init__(
        self,
        http: HttpPort,
        session: SessionPort,
        outbox: OutboxPort,
        sync_state: SyncStatePort,
    ) -> None:
        self._http = http
        self._session = session
        self._outbox = outbox
        self._sync_state = sync_state

    def run(self) -> tuple[int, int]:
        jwt_token = self._session.get_jwt_token()
        if not jwt_token:
            raise RuntimeError("JWT token not available for sync push")

        pending = self._outbox.list_pending()
        if not pending:
            return 0, 0

        payload = {
            "items": [
                {
                    "table_name": row["table_name"],
                    "operation": row["operation"],
                    "record_uuid": row["record_uuid"],
                    "payload": row["payload"],
                }
                for row in pending
            ]
        }

        try:
            response = self._http.post(
                SYNC_PUSH_ENDPOINT,
                token=jwt_token,
                json=payload,
            )
        except Exception as exc:
            for row in pending:
                self._outbox.mark_failed(row["id"], str(exc))
            return 0, len(pending)

        accepted_uuids = set(response.get("accepted", []))
        failed_uuids = set(response.get("failed", []))
        rejected = response.get("rejected", {})

        accepted = 0
        failed = 0
        now = datetime.now(timezone.utc).isoformat()

        for row in pending:
            record_uuid = row["record_uuid"]
            outbox_id = row["id"]
            table_name = row["table_name"]

            if record_uuid in accepted_uuids:
                self._outbox.mark_done([outbox_id])
                try:
                    self._sync_state.mark_record_synced(table_name, record_uuid, now)
                except Exception:
                    pass
                accepted += 1
            else:
                if record_uuid in failed_uuids:
                    reason = "server rejected"
                else:
                    reason = rejected.get(record_uuid, "unknown error")
                self._outbox.mark_failed(outbox_id, reason)
                failed += 1

        return accepted, failed
