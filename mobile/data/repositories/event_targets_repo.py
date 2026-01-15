# mobile/data/repositories/event_targets_repo.py

"""
Responsibilities:
- Repository for event targets data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM inventory_event_targets_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO inventory_event_targets_local (
                uuid,
                server_id,
                event_uuid,
                product_uuid,
                expected_qty
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["event_uuid"],
                r["product_uuid"],
                r.get("expected_qty", 0),
            ),
        )

    conn.commit()
    conn.close()
