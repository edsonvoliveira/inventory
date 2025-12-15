# desktop/data/repositories/product_barcodes_repo.py

from desktop.data.db.connection import get_connection
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todos os códigos de barras locais pelos dados vindos do servidor.
    Usado em:
    - bootstrap inicial
    - full resync controlado
    """
    conn = get_connection()

    conn.execute("DELETE FROM product_barcodes_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO product_barcodes_local (
                uuid,
                server_id,
                product_uuid,
                barcode,
                is_active,
                synced
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["server_id"],           # id do barcode no Postgres
                r["product_uuid"],        # vínculo correto com produto local
                r["barcode"],
                1 if r.get("is_active", True) else 0,
            ),
        )

    conn.commit()
    conn.close()
