# desktop/data/repositories/zones_repo.py

from desktop.data.db.connection import get_connection
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todas as zonas locais pelos dados vindos do servidor.
    Usado em:
    - bootstrap inicial
    - full resync
    """
    conn = get_connection()

    conn.execute("DELETE FROM zones_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO zones_local (
                uuid,
                server_id,
                event_uuid,
                name,
                count_status,
                lock_status,
                synced
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["event_uuid"],
                r["name"],
                r.get("count_status"),
                r.get("lock_status"),
            ),
        )

    conn.commit()
    conn.close()
