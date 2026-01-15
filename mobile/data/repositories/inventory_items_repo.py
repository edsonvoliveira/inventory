# mobile/data/repositories/inventory_items_repo.py

"""
Responsibilities:
- Repository for inventory items data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def upsert_many(rows: list[dict]) -> None:
    if not rows:
        return
    conn = get_connection()
    sql = """
        INSERT INTO inventory_items_local (
            uuid,
            server_id,
            event_uuid,
            event_server_id,
            zone_uuid,
            zone_server_id,
            user_uuid,
            user_server_id,
            product_uuid,
            product_server_id,
            scanned_code,
            manual_sku,
            manual_name,
            qty_counted,
            batch_number,
            expiry_date,
            is_new_product,
            unknown_product,
            product_is_active_at_count,
            product_name_at_count,
            product_sku_at_count,
            device_timestamp,
            server_timestamp,
            device_id,
            latitude,
            longitude,
            source,
            audit_meta,
            created_at,
            updated_at,
            deleted_at,
            synced,
            synced_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            server_id=excluded.server_id,
            event_uuid=excluded.event_uuid,
            event_server_id=excluded.event_server_id,
            zone_uuid=excluded.zone_uuid,
            zone_server_id=excluded.zone_server_id,
            user_uuid=excluded.user_uuid,
            user_server_id=excluded.user_server_id,
            product_uuid=excluded.product_uuid,
            product_server_id=excluded.product_server_id,
            scanned_code=excluded.scanned_code,
            manual_sku=excluded.manual_sku,
            manual_name=excluded.manual_name,
            qty_counted=excluded.qty_counted,
            batch_number=excluded.batch_number,
            expiry_date=excluded.expiry_date,
            is_new_product=excluded.is_new_product,
            unknown_product=excluded.unknown_product,
            product_is_active_at_count=excluded.product_is_active_at_count,
            product_name_at_count=excluded.product_name_at_count,
            product_sku_at_count=excluded.product_sku_at_count,
            device_timestamp=excluded.device_timestamp,
            server_timestamp=excluded.server_timestamp,
            device_id=excluded.device_id,
            latitude=excluded.latitude,
            longitude=excluded.longitude,
            source=excluded.source,
            audit_meta=excluded.audit_meta,
            created_at=excluded.created_at,
            updated_at=excluded.updated_at,
            deleted_at=excluded.deleted_at,
            synced=excluded.synced,
            synced_at=excluded.synced_at
    """
    for r in rows:
        conn.execute(
            sql,
            (
                r["uuid"],
                r.get("server_id"),
                r["event_uuid"],
                r["event_server_id"],
                r["zone_uuid"],
                r["zone_server_id"],
                r["user_uuid"],
                r["user_server_id"],
                r.get("product_uuid"),
                r.get("product_server_id"),
                r.get("scanned_code"),
                r.get("manual_sku"),
                r.get("manual_name"),
                r.get("qty_counted", 0),
                r.get("batch_number"),
                r.get("expiry_date"),
                r.get("is_new_product", 0),
                r.get("unknown_product", 0),
                r.get("product_is_active_at_count"),
                r.get("product_name_at_count"),
                r.get("product_sku_at_count"),
                r.get("device_timestamp"),
                r.get("server_timestamp"),
                r.get("device_id"),
                r.get("latitude"),
                r.get("longitude"),
                r.get("source", "mobile"),
                r.get("audit_meta"),
                r.get("created_at"),
                r.get("updated_at"),
                r.get("deleted_at"),
                r.get("synced", 0),
                r.get("synced_at"),
            ),
        )
    conn.commit()
    conn.close()
