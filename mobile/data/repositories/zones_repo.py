from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM zones_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO zones_local (
                uuid,
                server_id,
                event_uuid,
                name,
                count_status,
                lock_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
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
