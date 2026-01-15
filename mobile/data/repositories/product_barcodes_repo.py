# mobile/data/repositories/product_barcodes_repo.py

"""
Responsibilities:
- Repository for product barcodes data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM product_barcodes_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO product_barcodes_local (
                uuid,
                server_id,
                product_uuid,
                barcode
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["product_uuid"],
                r["barcode"],
            ),
        )

    conn.commit()
    conn.close()
