# mobile/data/repositories/locations_repo.py

"""
Responsibilities:
- Repository for locations data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def upsert_many(rows: list[dict]) -> None:
    if not rows:
        return
    conn = get_connection()
    sql = """
        INSERT INTO locations_local (
            uuid,
            server_id,
            company_server_id,
            code,
            name,
            address,
            is_active,
            updated_at,
            deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(server_id) DO UPDATE SET
            uuid=excluded.uuid,
            company_server_id=excluded.company_server_id,
            code=excluded.code,
            name=excluded.name,
            address=excluded.address,
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
                r.get("code"),
                r["name"],
                r.get("address"),
                r.get("is_active", 1),
                r.get("updated_at"),
                r.get("deleted_at"),
            ),
        )
    conn.commit()
    conn.close()
