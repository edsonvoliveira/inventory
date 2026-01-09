# desktop/core/sync_push_service.py
"""
Responsibilities:
- Orchestrating sync push
- Getting last sync timestamp (last_pull_at)
- Call endpoint and call apply pull payload
- Update meta
"""

from desktop.data.repositories.outbox_repo import OutboxRepo
from desktop.data.db.connection import get_connection
from desktop.core.http_client import post
from desktop.core.session_service import SessionService

SYNC_PUSH_ENDPOINT = "/v1/sync/push"

class SyncPushService:
    """
    Responsável por enviar alterações locais (outbox) ao DV Server.
    """

    def run(self) -> tuple[int, int]:
        jwt_token = SessionService.get_jwt_token()
        if not jwt_token:
            raise RuntimeError("JWT token não disponível para sync push")

        conn = get_connection()
        outbox_repo = OutboxRepo(conn)

        pending = outbox_repo.get_pending()
        if not pending:
            return 0, 0

        payload = {
            "items": [
                {
                    "table": row["table_name"],
                    "operation": row["operation"],
                    "uuid": row["record_uuid"],
                    "payload": row["payload"],
                }
                for row in pending
            ]
        }

        accepted = 0
        failed = 0

        try:
            response = post(
                SYNC_PUSH_ENDPOINT,
                jwt_token=jwt_token,
                json_body=payload,
            )

        except Exception as e:
            for row in pending:
                outbox_repo.mark_failed(row["id"], str(e))
            return 0, len(pending)

        accepted_uuids = set(response.get("accepted", []))
        rejected = response.get("rejected", {})

        for row in pending:
            record_uuid = row["record_uuid"]
            outbox_id = row["id"]

            if record_uuid in accepted_uuids:
                outbox_repo.mark_success(outbox_id)
                accepted += 1
            else:
                reason = rejected.get(record_uuid, "unknown error")
                outbox_repo.mark_failed(outbox_id, reason)
                failed += 1

        return accepted, failed
