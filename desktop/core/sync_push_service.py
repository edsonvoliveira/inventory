# desktop/core/sync_push_service.py

"""
Responsibilities:
- Service layer for sync push workflows.
- Coordinate related operations and dependencies.
"""

from datetime import datetime, timezone
import sqlite3

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
            conn.close()
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
            conn.commit()
            conn.close()
            return 0, len(pending)

        accepted_uuids = set(response.get("accepted", []))
        failed_uuids = set(response.get("failed", []))
        rejected = response.get("rejected", {})

        now = datetime.now(timezone.utc).isoformat()
        for row in pending:
            record_uuid = row["record_uuid"]
            outbox_id = row["id"]
            table_name = row["table_name"]

            if record_uuid in accepted_uuids:
                outbox_repo.mark_success([outbox_id])
                try:
                    conn.execute(
                        f"UPDATE {table_name}_local SET synced = 1, synced_at = ? WHERE uuid = ?",
                        (now, record_uuid),
                    )
                except sqlite3.Error:
                    pass
                accepted += 1
            else:
                if record_uuid in failed_uuids:
                    reason = "server rejected"
                else:
                    reason = rejected.get(record_uuid, "unknown error")
                outbox_repo.mark_failed(outbox_id, reason)
                failed += 1

        conn.commit()
        conn.close()
        return accepted, failed
