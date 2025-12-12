from desktop.data.db.connection import get_connection

def replace_all(rows: list[dict]):
    conn = get_connection()
    conn.execute("DELETE FROM companies_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO companies_local (uuid, server_id, name, vat_number, is_active, synced)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["name"],
                r.get("vat_number"),
                r.get("is_active", 1),
            ),
        )

    conn.commit()
    conn.close()
