# mobile/data/repositories/product_barcodes_repo.py

"""
Responsibilities:
- Repository for product barcodes data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def _resolve_product_uuid(row: dict) -> str:
    product_uuid = row.get("product_uuid")
    if product_uuid:
        return product_uuid
    product_server_id = row.get("product_server_id")
    if product_server_id is None:
        raise KeyError("product_uuid or product_server_id required for barcode")
    return f"server:{product_server_id}"


def replace_all(rows: list[dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM product_barcodes_local")
    for r in rows:
        cur.execute(
            """
            INSERT INTO product_barcodes_local (
                uuid,
                server_id,
                company_server_id,
                product_uuid,
                product_server_id,
                barcode,
                description,
                is_active,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["company_server_id"],
                _resolve_product_uuid(r),
                r.get("product_server_id"),
                r["barcode"],
                r.get("description"),
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
        INSERT INTO product_barcodes_local (
            uuid,
            server_id,
            company_server_id,
            product_uuid,
            product_server_id,
            barcode,
            description,
            is_active,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            uuid=excluded.uuid,
            server_id=excluded.server_id,
            company_server_id=excluded.company_server_id,
            product_uuid=excluded.product_uuid,
            product_server_id=excluded.product_server_id,
            barcode=excluded.barcode,
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
                _resolve_product_uuid(r),
                r.get("product_server_id"),
                r["barcode"],
                r.get("description"),
                r.get("is_active", 1),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()
