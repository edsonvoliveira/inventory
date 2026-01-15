# mobile/data/repositories/zone_user_progress_repo.py

"""
Responsibilities:
- Repository for zone user progress data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def upsert_many(rows: list[dict]) -> None:
    if not rows:
        return
    conn = get_connection()
    sql = """
        INSERT INTO zone_user_progress_local (
            uuid,
            server_id,
            event_uuid,
            event_server_id,
            zone_uuid,
            zone_server_id,
            user_uuid,
            user_server_id,
            count_type,
            started_at,
            finished_at,
            is_finished,
            items_counted,
            qty_total,
            device_id,
            created_at,
            updated_at,
            deleted_at,
            source,
            synced,
            synced_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            server_id=excluded.server_id,
            event_uuid=excluded.event_uuid,
            event_server_id=excluded.event_server_id,
            zone_uuid=excluded.zone_uuid,
            zone_server_id=excluded.zone_server_id,
            user_uuid=excluded.user_uuid,
            user_server_id=excluded.user_server_id,
            count_type=excluded.count_type,
            started_at=excluded.started_at,
            finished_at=excluded.finished_at,
            is_finished=excluded.is_finished,
            items_counted=excluded.items_counted,
            qty_total=excluded.qty_total,
            device_id=excluded.device_id,
            created_at=excluded.created_at,
            updated_at=excluded.updated_at,
            deleted_at=excluded.deleted_at,
            source=excluded.source,
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
                r.get("count_type"),
                r.get("started_at"),
                r.get("finished_at"),
                r.get("is_finished", 0),
                r.get("items_counted", 0),
                r.get("qty_total", 0),
                r.get("device_id"),
                r.get("created_at"),
                r.get("updated_at"),
                r.get("deleted_at"),
                r.get("source", "mobile"),
                r.get("synced", 0),
                r.get("synced_at"),
            ),
        )
    conn.commit()
    conn.close()
