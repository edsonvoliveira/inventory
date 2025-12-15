# desktop/data/repositories/companies_repo.py
from desktop.data.db.connection import get_connection

def replace_all(rows: list[dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM companies_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO companies_local (
                uuid,
                server_id,
                name,
                vat_number,
                is_active,
                synced
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["name"],
                r.get("vat_number"),
                1 if r.get("is_active", True) else 0,
            ),
        )

    conn.commit()
    conn.close()
