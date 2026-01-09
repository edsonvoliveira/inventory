# desktop/data/repositories/zone_user_progress_repo.py

import json
import uuid
from datetime import datetime, timezone

from desktop.data.db.connection import get_connection


def start_zone(
    *,
    zone_uuid: str,
    user_uuid: str,
    device_id: str | None = None,
) -> str:
    """
    Registra o início da contagem de uma zona por um usuário.
    Retorna o UUID da sessão criada.
    """

    progress_uuid = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "uuid": progress_uuid,
        "zone_uuid": zone_uuid,
        "user_uuid": user_uuid,
        "started_at": now,
        "device_id": device_id,
    }

    conn = get_connection()

    # 1️⃣ Inserir progresso local
    conn.execute(
        """
        INSERT INTO zone_user_progress_local (
            uuid,
            zone_uuid,
            user_uuid,
            started_at,
            is_finished,
            synced
        )
        VALUES (?, ?, ?, ?, 0, 0)
        """,
        (
            progress_uuid,
            zone_uuid,
            user_uuid,
            now,
        ),
    )

    # 2️⃣ Criar outbox
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
        (
            "zone_user_progress",
            "insert",
            progress_uuid,
            json.dumps(payload),
        ),
    )

    conn.commit()
    conn.close()

    return progress_uuid


def finish_zone(
    *,
    progress_uuid: str,
):
    """
    Finaliza a contagem de uma zona.
    """

    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "uuid": progress_uuid,
        "finished_at": now,
        "is_finished": True,
    }

    conn = get_connection()

    # 1️⃣ Atualizar progresso local
    conn.execute(
        """
        UPDATE zone_user_progress_local
        SET finished_at = ?,
            is_finished = 1,
            synced = 0
        WHERE uuid = ?
        """,
        (
            now,
            progress_uuid,
        ),
    )

    # 2️⃣ Criar outbox
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
        (
            "zone_user_progress",
            "update",
            progress_uuid,
            json.dumps(payload),
        ),
    )

    conn.commit()
    conn.close()


def mark_as_synced(*, uuid: str, server_id: int):
    conn = get_connection()
    conn.execute(
        """
        UPDATE zone_user_progress_local
        SET server_id = ?, synced = 1, synced_at = ?
        WHERE uuid = ?
        """,
        (server_id, datetime.now(timezone.utc).isoformat(), uuid),
    )
    conn.commit()
    conn.close()
