# mobile/data/repositories/users_repo.py

"""
Responsibilities:
- Repository for users data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users_local")
    for r in rows:
        cur.execute(
            """
            INSERT INTO users_local (
                uuid,
                server_id,
                company_server_id,
                name,
                role,
                is_active,
                updated_at,
                deleted_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["company_server_id"],
                r["name"],
                r["role"],
                r.get("is_active", 1),
                r.get("updated_at"),
                r.get("deleted_at"),
            ),
        )
    conn.commit()
    conn.close()


def upsert_many(rows: list[dict]) -> None:
    if not rows:
        return
    conn = get_connection()
    sql = """
        INSERT INTO users_local (
            uuid,
            server_id,
            company_server_id,
            name,
            role,
            is_active,
            updated_at,
            deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(server_id) DO UPDATE SET
            uuid=excluded.uuid,
            company_server_id=excluded.company_server_id,
            name=excluded.name,
            role=excluded.role,
            is_active=excluded.is_active,
            updated_at=excluded.updated_at,
            deleted_at=excluded.deleted_at
    """
    for r in rows:
        conn.execute(
            sql,
            (
                r["uuid"],
                r["server_id"],
                r["company_server_id"],
                r["name"],
                r["role"],
                r.get("is_active", 1),
                r.get("updated_at"),
                r.get("deleted_at"),
            ),
        )
    conn.commit()
    conn.close()
