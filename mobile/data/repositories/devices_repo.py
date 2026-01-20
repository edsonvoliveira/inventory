# mobile/data/repositories/devices_repo.py

"""
Responsibilities:
- Repository for devices data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def upsert_many(rows: list[dict]) -> None:
    if not rows:
        return
    conn = get_connection()
    sql = """
        INSERT INTO devices_local (
            uuid,
            server_id,
            device_uuid,
            os,
            app_version,
            is_blocked,
            last_sync_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            uuid=excluded.uuid,
            server_id=excluded.server_id,
            device_uuid=excluded.device_uuid,
            os=excluded.os,
            app_version=excluded.app_version,
            is_blocked=excluded.is_blocked,
            last_sync_at=excluded.last_sync_at,
            updated_at=excluded.updated_at
    """
    for r in rows:
        conn.execute(
            sql,
            (
                r["uuid"],
                r.get("server_id"),
                r["device_uuid"],
                r.get("os"),
                r.get("app_version"),
                r.get("is_blocked", 0),
                r.get("last_sync_at"),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()
