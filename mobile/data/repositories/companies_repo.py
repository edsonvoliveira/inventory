# mobile/data/repositories/companies_repo.py

"""
Responsibilities:
- Repository for companies data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM companies_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO companies_local (
                uuid,
                server_id,
                name
            )
            VALUES (?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["name"],
            ),
        )

    conn.commit()
    conn.close()
