# desktop/data/outbox/outbox_repo.py

import json
from typing import Any, Dict, List

from desktop.data.db.connection import get_connection


def add_outbox_record(
    table_name: str,
    operation: str,
    record_uuid: str,
    payload: Dict[str, Any],
) -> None:
    """
    Regista uma operação pendente na outbox_local.

    table_name: nome lógico da tabela (ex: "inventory_items")
    operation : "insert" | "update" | "delete"
    record_uuid: UUID da linha no contexto da tabela
    payload   : JSON com os dados relevantes para o DV Server
    """
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO outbox_local (
            table_name,
            operation,
            record_uuid,
            payload
        )
        VALUES (?, ?, ?, ?)
        """,
        (table_name, operation, record_uuid, json.dumps(payload)),
    )
    conn.commit()
    conn.close()


def get_pending(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Devolve uma lista de registos ainda não sincronizados
    (tentativas < 5), ordenados por id.
    """
    conn = get_connection()
    cur = conn.execute(
        """
        SELECT
          id,
          table_name,
          operation,
          record_uuid,
          payload,
          attempts
        FROM outbox_local
        WHERE attempts < 5
        ORDER BY id
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    pending: List[Dict[str, Any]] = []
    for row in rows:
        (
            outbox_id,
            table_name,
            operation,
            record_uuid,
            payload_json,
            attempts,
        ) = row

        try:
            payload = json.loads(payload_json) if payload_json else {}
        except Exception:
            payload = {}

        pending.append(
            {
                "id": outbox_id,
                "table_name": table_name,
                "operation": operation,
                "record_uuid": record_uuid,
                "payload": payload,
                "attempts": attempts,
            }
        )

    return pending


def mark_success(ids: List[int]) -> None:
    """
    Remove da outbox os registos que foram aceites pelo DV Server.
    """
    if not ids:
        return

    conn = get_connection()
    conn.executemany(
        "DELETE FROM outbox_local WHERE id = ?",
        [(i,) for i in ids],
    )
    conn.commit()
    conn.close()


def mark_failed(outbox_id: int, error: str) -> None:
    """
    Marca um registo como falhado, incrementando o número de tentativas
    e guardando a última mensagem de erro.
    """
    conn = get_connection()
    conn.execute(
        """
        UPDATE outbox_local
        SET attempts   = attempts + 1,
            last_error = ?
        WHERE id = ?
        """,
        (error, outbox_id),
    )
    conn.commit()
    conn.close()
