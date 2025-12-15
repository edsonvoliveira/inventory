# desktop/data/repositories/products_repo.py

from desktop.data.db.connection import get_connection
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todos os produtos locais pelos dados vindos do servidor.
    Usado em:
    - bootstrap inicial
    - full resync controlado
    """
    conn = get_connection()

    conn.execute("DELETE FROM products_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO products_local (
                uuid,
                server_id,
                sku,
                name,
                uom_inventory,
                system_qty,
                serial_number_enabled,
                is_active,
                synced
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["server_id"],                       # id do produto no Postgres
                r["sku"],
                r["name"],
                r.get("uom_inventory"),
                r.get("system_qty", 0),
                1 if r.get("serial_number_enabled", False) else 0,
                1 if r.get("is_active", True) else 0,
            ),
        )

    conn.commit()
    conn.close()
