# desktop/data/repositories/product_categories_repo.py

from desktop.data.db.connection import get_connection
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todas as categorias locais pelos dados vindos do servidor.
    Usado apenas em:
    - bootstrap inicial
    - full resync controlado
    """
    conn = get_connection()

    conn.execute("DELETE FROM product_categories_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO product_categories_local (
                uuid,
                server_id,
                code,
                name,
                is_active,
                synced
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["id"],          # id da categoria no Postgres
                r.get("code"),
                r["name"],
                1 if r.get("is_active", True) else 0,
            ),
        )

    conn.commit()
    conn.close()
