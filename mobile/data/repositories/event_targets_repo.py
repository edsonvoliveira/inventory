# mobile/data/repositories/event_targets_repo.py

"""
Responsibilities:
- Repository for event targets data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def _resolve_event_uuid(row: dict) -> str:
    event_uuid = row.get("event_uuid")
    if event_uuid:
        return event_uuid
    event_server_id = row.get("event_server_id")
    if event_server_id is None:
        raise KeyError("event_uuid or event_server_id required for event target")
    return f"server:{event_server_id}"


def _resolve_product_uuid(row: dict) -> str:
    product_uuid = row.get("product_uuid")
    if product_uuid:
        return product_uuid
    product_server_id = row.get("product_server_id")
    if product_server_id is None:
        raise KeyError("product_uuid or product_server_id required for event target")
    return f"server:{product_server_id}"


def replace_all(rows: list[dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory_event_targets_local")
    for r in rows:
        cur.execute(
            """
            INSERT INTO inventory_event_targets_local (
                uuid,
                server_id,
                company_server_id,
                event_uuid,
                event_server_id,
                product_uuid,
                product_server_id,
                expected_qty,
                is_active,
                updated_at,
                deleted_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["company_server_id"],
                _resolve_event_uuid(r),
                r.get("event_server_id"),
                _resolve_product_uuid(r),
                r.get("product_server_id"),
                r.get("expected_qty", 0),
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
        INSERT INTO inventory_event_targets_local (
            uuid,
            server_id,
            company_server_id,
            event_uuid,
            event_server_id,
            product_uuid,
            product_server_id,
            expected_qty,
            is_active,
            updated_at,
            deleted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(server_id) DO UPDATE SET
            uuid=excluded.uuid,
            company_server_id=excluded.company_server_id,
            event_uuid=excluded.event_uuid,
            event_server_id=excluded.event_server_id,
            product_uuid=excluded.product_uuid,
            product_server_id=excluded.product_server_id,
            expected_qty=excluded.expected_qty,
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
                _resolve_event_uuid(r),
                r.get("event_server_id"),
                _resolve_product_uuid(r),
                r.get("product_server_id"),
                r.get("expected_qty", 0),
                r.get("is_active", 1),
                r.get("updated_at"),
                r.get("deleted_at"),
            ),
        )
    conn.commit()
    conn.close()
