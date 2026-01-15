# mobile/data/repositories/events_repo.py

"""
Responsibilities:
- Repository for events data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM inventory_events_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO inventory_events_local (
                uuid,
                server_id,
                title,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["title"],
                r["status"],
            ),
        )

    conn.commit()
    conn.close()
