# desktop/data/repositories/outbox_repo.py

"""
Responsibilities:
- Repository for outbox data.
- Define persistence and sync behavior.
"""

#desktop/data/repositories/outbox_repo.py

"""
Responsabilities:
- Repository for outbox entity
- Manages outbox messages for sync operations
- Provides methods to add, retrieve, mark success/failure, and delete outbox records
"""

import json
from typing import Iterable, Optional


class OutboxRepo:
    def __init__(self, conn):
        self.conn = conn

    # --------------------------------------------------
    # Escrita (usada indiretamente pelos repos via BaseRepo)
    # --------------------------------------------------
    def add(
        self,
        table_name: str,
        operation: str,
        record_uuid: str,
        payload: dict,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO outbox_local (
                table_name,
                operation,
                record_uuid,
                payload
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                table_name,
                operation,
                record_uuid,
                json.dumps(payload),
            ),
        )
        return cur.lastrowid

    # --------------------------------------------------
    # Leitura (Sync Push)
    # --------------------------------------------------
    def get_pending(self, limit: int = 100) -> list[dict]:
        rows = self.conn.execute(
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

    # --------------------------------------------------
    # Sucesso / Falha
    # --------------------------------------------------
    def mark_success(self, ids: Iterable[int]) -> None:
        ids = list(ids)
        if not ids:
            return

        placeholders = ",".join("?" for _ in ids)
        self.conn.execute(
            f"DELETE FROM outbox_local WHERE id IN ({placeholders})",
            ids,
        )

    def mark_failed(self, id_: int, error: str) -> None:
        row = self.conn.execute(
            "SELECT attempts, max_attempts FROM outbox_local WHERE id = ?",
            (id_,),
        ).fetchone()
        if not row:
            return
        attempts, max_attempts = row
        new_attempts = (attempts or 0) + 1
        is_dead = new_attempts >= (max_attempts or 0)
        forced_dead = error.startswith("auth") or error.startswith("validation")
        status = "error" if (is_dead or forced_dead) else "pending"
        self.conn.execute(
            """
            UPDATE outbox_local
            SET attempts = ?,
                status = ?,
                last_error = ?
            WHERE id = ?
            """,
            (new_attempts, status, error, id_),
        )

    # --------------------------------------------------
    # Administração
    # --------------------------------------------------
    def delete_all(self) -> None:
        self.conn.execute("DELETE FROM outbox_local")
