from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO users_local (
                uuid,
                server_id,
                name,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["name"],
                r["role"],
            ),
        )

    conn.commit()
    conn.close()
