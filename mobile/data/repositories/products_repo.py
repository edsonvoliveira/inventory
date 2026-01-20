# mobile/data/repositories/products_repo.py

"""
Responsibilities:
- Repository for products data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products_local")
    for r in rows:
        cur.execute(
            """
            INSERT INTO products_local (
                uuid,
                server_id,
                company_server_id,
                category_server_id,
                sku,
                name,
                description,
                uom_base,
                uom_inventory,
                conversion_factor,
                system_qty,
                is_sensitive,
                serial_number_enabled,
                is_active,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["company_server_id"],
                r.get("category_server_id"),
                r["sku"],
                r["name"],
                r.get("description"),
                r.get("uom_base"),
                r.get("uom_inventory"),
                r.get("conversion_factor", 1),
                r.get("system_qty", 0),
                r.get("is_sensitive", 0),
                r.get("serial_number_enabled", 0),
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
        INSERT INTO products_local (
            uuid,
            server_id,
            company_server_id,
            category_server_id,
            sku,
            name,
            description,
            uom_base,
            uom_inventory,
            conversion_factor,
            system_qty,
            is_sensitive,
            serial_number_enabled,
            is_active,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            uuid=excluded.uuid,
            server_id=excluded.server_id,
            company_server_id=excluded.company_server_id,
            category_server_id=excluded.category_server_id,
            sku=excluded.sku,
            name=excluded.name,
            description=excluded.description,
            uom_base=excluded.uom_base,
            uom_inventory=excluded.uom_inventory,
            conversion_factor=excluded.conversion_factor,
            system_qty=excluded.system_qty,
            is_sensitive=excluded.is_sensitive,
            serial_number_enabled=excluded.serial_number_enabled,
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
                r.get("category_server_id"),
                r["sku"],
                r["name"],
                r.get("description"),
                r.get("uom_base"),
                r.get("uom_inventory"),
                r.get("conversion_factor", 1),
                r.get("system_qty", 0),
                r.get("is_sensitive", 0),
                r.get("serial_number_enabled", 0),
                r.get("is_active", 1),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()
