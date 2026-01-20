# mobile/data/repositories/zones_repo.py

"""
Responsibilities:
- Repository for zones data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def _resolve_event_uuid(row: dict) -> str:
    event_uuid = row.get("event_uuid")
    if event_uuid:
        return event_uuid
    event_server_id = row.get("event_server_id")
    if event_server_id is None:
        raise KeyError("event_uuid or event_server_id required for zone")
    return f"server:{event_server_id}"


def replace_all(rows: list[dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM zones_local")
    for r in rows:
        cur.execute(
            """
            INSERT INTO zones_local (
                uuid,
                server_id,
                event_uuid,
                event_server_id,
                name,
                description,
                count_status,
                lock_status,
                is_active,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                _resolve_event_uuid(r),
                r.get("event_server_id"),
                r["name"],
                r.get("description"),
                r.get("count_status"),
                r.get("lock_status"),
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
        INSERT INTO zones_local (
            uuid,
            server_id,
            event_uuid,
            event_server_id,
            name,
            description,
            count_status,
            lock_status,
            is_active,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            uuid=excluded.uuid,
            server_id=excluded.server_id,
            event_uuid=excluded.event_uuid,
            event_server_id=excluded.event_server_id,
            name=excluded.name,
            description=excluded.description,
            count_status=excluded.count_status,
            lock_status=excluded.lock_status,
            is_active=excluded.is_active,
            updated_at=excluded.updated_at
    """
    for r in rows:
        conn.execute(
            sql,
            (
                r["uuid"],
                r["server_id"],
                _resolve_event_uuid(r),
                r.get("event_server_id"),
                r["name"],
                r.get("description"),
                r.get("count_status"),
                r.get("lock_status"),
                r.get("is_active", 1),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()
