# mobile/data/repositories/product_categories_repo.py

"""
Responsibilities:
- Repository for product categories data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def upsert_many(rows: list[dict]) -> None:
    if not rows:
        return
    conn = get_connection()
    sql = """
        INSERT INTO product_categories_local (
            uuid,
            server_id,
            company_server_id,
            code,
            name,
            description,
            is_active,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            uuid=excluded.uuid,
            server_id=excluded.server_id,
            company_server_id=excluded.company_server_id,
            code=excluded.code,
            name=excluded.name,
            description=excluded.description,
            is_active=excluded.is_active,
            updated_at=excluded.updated_at
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
                r.get("description"),
                r.get("is_active", 1),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()
