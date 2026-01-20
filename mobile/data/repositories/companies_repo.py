# mobile/data/repositories/companies_repo.py

"""
Responsibilities:
- Repository for companies data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


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
                is_active,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["name"],
                r.get("is_active", 1),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()


def upsert_many(rows: list[dict]) -> None:
    if not rows:
        return
    conn = get_connection()
    sql = """
        INSERT INTO companies_local (
            uuid,
            server_id,
            name,
            is_active,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            uuid=excluded.uuid,
            server_id=excluded.server_id,
            name=excluded.name,
            is_active=excluded.is_active,
            updated_at=excluded.updated_at
    """
    for r in rows:
        conn.execute(
            sql,
            (
                r["uuid"],
                r["server_id"],
                r["name"],
                r.get("is_active", 1),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()
