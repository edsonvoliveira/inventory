# desktop/data/repositories/inventory_event_targets_repo.py

from desktop.data.db.connection import get_connection
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todos os targets locais pelos dados vindos do servidor.
    Usado em:
    - bootstrap inicial
    - full resync
    """
    conn = get_connection()

    conn.execute("DELETE FROM inventory_event_targets_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO inventory_event_targets_local (
                uuid,
                server_id,
                event_uuid,
                product_uuid,
                expected_qty,
                synced
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["id"],
                r["event_uuid"],
                r["product_uuid"],
                r.get("expected_qty", 0),
            ),
        )

    conn.commit()
    conn.close()
