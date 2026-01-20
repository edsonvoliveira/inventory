from __future__ import annotations

from datetime import datetime, timezone

from app_core.ports.http_port import HttpPort
from app_core.ports.session_port import SessionPort
from app_core.ports.outbox_port import OutboxPort
from app_core.ports.sync_state_port import SyncStatePort

DEFAULT_PUSH_ENDPOINT = "/v1/sync/push"


def _classify_exception(exc: Exception) -> str:
    msg = str(exc)
    lowered = msg.lower()
    if "401" in lowered or "403" in lowered or "jwt" in lowered:
        return f"auth:{msg}"
    return f"transient:{msg}"


class SyncPushService:
    def __init__(
        self,
        http: HttpPort,
        session: SessionPort,
        outbox: OutboxPort,
        sync_state: SyncStatePort,
        endpoint: str | None = None,
    ) -> None:
        self._http = http
        self._session = session
        self._outbox = outbox
        self._sync_state = sync_state
        self._endpoint = endpoint or DEFAULT_PUSH_ENDPOINT

    def run(self, *, correlation_id: str | None = None) -> tuple[int, int]:
        jwt_token = self._session.get_jwt_token()
        if not jwt_token:
            raise RuntimeError("JWT token not available for sync push")

        pending = self._outbox.list_pending()
        if not pending:
            return 0, 0

        accepted = 0
        failed = 0
        now = datetime.now(timezone.utc).isoformat()

        for row in pending:
            record_uuid = row["record_uuid"]
            outbox_id = row["id"]
            table_name = row["table_name"]
            item_payload = row["payload"]
            if isinstance(item_payload, dict):
                item_payload = dict(item_payload)
                item_payload.pop("deleted_at", None)
                if row["operation"] == "update" and "client_updated_at" not in item_payload:
                    item_payload["client_updated_at"] = now

            payload = {
                "items": [
                    {
                        "table_name": row["table_name"],
                        "operation": row["operation"],
                        "record_uuid": record_uuid,
                        "payload": item_payload,
                    }
                ]
            }

            headers = {}
            if correlation_id:
                headers["X-Correlation-Id"] = correlation_id

            try:
                response = self._http.post(
                    self._endpoint,
                    token=jwt_token,
                    json=payload,
                    headers=headers,
                )
            except Exception as exc:
                reason = _classify_exception(exc)
                self._outbox.mark_failed(outbox_id, reason)
                failed += 1
                continue

            accepted_uuids = set(response.get("accepted", []))
            failed_uuids = set(response.get("failed", []))
            raw_rejected = response.get("rejected", {})
            rejected = raw_rejected if isinstance(raw_rejected, dict) else {}
            raw_server_ids = response.get("server_ids", {})
            server_ids = raw_server_ids if isinstance(raw_server_ids, dict) else {}

            if record_uuid in accepted_uuids:
                self._outbox.mark_done([outbox_id])
                try:
                    self._sync_state.mark_record_synced(table_name, record_uuid, now)
                except Exception:
                    pass
                server_id = server_ids.get(record_uuid)
                if server_id is not None:
                    try:
                        self._sync_state.set_record_server_id(table_name, record_uuid, int(server_id))
                    except Exception:
                        pass
                accepted += 1
            else:
                if record_uuid in failed_uuids:
                    reason = "validation:server_rejected"
                else:
                    reason = rejected.get(record_uuid, "unknown error")
                    if reason and reason != "unknown error":
                        reason = f"validation:{reason}"
                self._outbox.mark_failed(outbox_id, reason)
                failed += 1

        return accepted, failed
