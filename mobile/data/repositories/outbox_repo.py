# mobile/data/repositories/outbox_repo.py

"""
Responsibilities:
- Repository for outbox data.
- Define persistence and sync behavior.
"""

import json
from typing import Iterable

from mobile.data.db.connection import get_connection


def add(table_name: str, operation: str, record_uuid: str, payload: dict) -> int:
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO outbox_local (table_name, operation, record_uuid, payload)
        VALUES (?, ?, ?, ?)
        """,
        (table_name, operation, record_uuid, json.dumps(payload)),
    )
    conn.commit()
    row_id = cur.lastrowid
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
            attempts,
            last_error
        FROM outbox_local
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
            "attempts": r[5],
            "last_error": r[6],
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
    conn.execute(
        """
        UPDATE outbox_local
        SET attempts = attempts + 1,
            last_error = ?
        WHERE id = ?
        """,
        (error, outbox_id),
    )
    conn.commit()
    conn.close()
