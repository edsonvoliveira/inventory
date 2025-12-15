# desktop/core/sync_push_service.py

import json
from typing import List, Dict

from desktop.data.db.connection import get_connection
from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT


def sync_push(jwt_token: str) -> bool:
    """
    Envia os registros pendentes da outbox_local para o DV Server.
    """

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT id, table_name, operation, record_uuid, payload
        FROM outbox_local
        ORDER BY created_at ASC
        """
    ).fetchall()

    if not rows:
        conn.close()
        return True  # nada a sincronizar

    items: List[Dict] = []

    for r in rows:
        items.append(
            {
                "table_name": r["table_name"],
                "operation": r["operation"],
                "record_uuid": r["record_uuid"],
                "payload": json.loads(r["payload"]),
            }
        )

    response = post(
        SYNC_PUSH_ENDPOINT,
        jwt_token,
        json_body={"items": items},
    )

    accepted = response.get("accepted", [])

    # Marcar como sincronizados
    for uuid in accepted:
        conn.execute(
            """
            DELETE FROM outbox_local
            WHERE record_uuid = ?
            """,
            (uuid,),
        )

    conn.commit()
    conn.close()

    return True
