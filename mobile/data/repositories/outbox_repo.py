# mobile/data/repositories/outbox_repo.py

"""
Responsibilities:
- Repository for outbox data.
- Define persistence and sync behavior.
"""

import json
from typing import Iterable

from mobile.data.db.connection import get_connection

_ALLOWED_MOBILE_ENTITIES = {"inventory_items", "zone_user_progress", "devices"}
_ZONE_USER_PROGRESS_ALLOWLIST = {
    "zone_id",
    "user_id",
    "count_type",
    "started_at",
    "finished_at",
    "is_finished",
    "items_counted",
    "qty_total",
    "device_id",
    "device_timestamp",
    "source",
}


def add(
    table_name: str,
    operation: str,
    record_uuid: str,
    payload: dict,
    *,
    conn=None,
) -> int:
    if table_name not in _ALLOWED_MOBILE_ENTITIES:
        raise RuntimeError("outbox entity not allowed for mobile")
    if table_name == "zone_user_progress":
        payload = {k: v for k, v in payload.items() if k in _ZONE_USER_PROGRESS_ALLOWLIST}
    owns_conn = conn is None
    if owns_conn:
        conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO outbox_local (table_name, operation, record_uuid, payload)
        VALUES (?, ?, ?, ?)
        """,
        (table_name, operation, record_uuid, json.dumps(payload)),
    )
    if owns_conn:
        conn.commit()
    row_id = cur.lastrowid
    if owns_conn:
        conn.close()
    return row_id


def get_pending(limit: int = 100) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            id,
            table_name,
            operation,
            record_uuid,
            payload,
            status,
            attempts,
            max_attempts,
            last_error
        FROM outbox_local
        WHERE status = 'pending'
        ORDER BY id
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "table_name": r[1],
            "operation": r[2],
            "record_uuid": r[3],
            "payload": json.loads(r[4]),
            "status": r[5],
            "attempts": r[6],
            "max_attempts": r[7],
            "last_error": r[8],
        }
        for r in rows
    ]


def mark_success(ids: Iterable[int]) -> None:
    ids = list(ids)
    if not ids:
        return
    conn = get_connection()
    placeholders = ",".join("?" for _ in ids)
    conn.execute(
        f"DELETE FROM outbox_local WHERE id IN ({placeholders})",
        ids,
    )
    conn.commit()
    conn.close()


def mark_failed(outbox_id: int, error: str) -> None:
    conn = get_connection()
    row = conn.execute(
        "SELECT attempts, max_attempts FROM outbox_local WHERE id = ?",
        (outbox_id,),
    ).fetchone()
    if not row:
        conn.close()
        return
    attempts, max_attempts = row
    new_attempts = (attempts or 0) + 1
    is_dead = new_attempts >= (max_attempts or 0)
    forced_dead = error.startswith("auth") or error.startswith("validation")
    status = "error" if (is_dead or forced_dead) else "pending"
    conn.execute(
        """
        UPDATE outbox_local
        SET attempts = ?,
            status = ?,
            last_error = ?
        WHERE id = ?
        """,
        (new_attempts, status, error, outbox_id),
    )
    conn.commit()
    conn.close()
