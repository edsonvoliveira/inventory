# mobile/data/repositories/products_repo.py

"""
Responsibilities:
- Repository for products data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection

def replace_all(rows: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM products_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO products_local (
                uuid, server_id, sku, name, is_active
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["sku"],
                r["name"],
                r.get("is_active", 1),
            ),
        )

    conn.commit()
    conn.close()
