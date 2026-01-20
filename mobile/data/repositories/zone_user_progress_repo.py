# mobile/data/repositories/zone_user_progress_repo.py

"""
Responsibilities:
- Repository for zone user progress data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def _to_uuid(value: int) -> str:
    return f"server:{value}"

def _parse_server_uuid(value: str | None) -> int | None:
    if not value:
        return None
    if value.startswith("server:"):
        raw = value.split("server:", 1)[1]
        if raw.isdigit():
            return int(raw)
    return None


def _resolve_event_server_id(conn, row: dict) -> int:
    event_server_id = row.get("event_server_id")
    if event_server_id is not None:
        return int(event_server_id)

    parsed = _parse_server_uuid(row.get("event_uuid"))
    if parsed is not None:
        return parsed

    zone_server_id = row.get("zone_server_id")
    if zone_server_id is None:
        raise KeyError("event_server_id or zone_server_id required for zone_user_progress")

    row_db = conn.execute(
        "SELECT event_server_id FROM zones_local WHERE server_id = ?",
        (zone_server_id,),
    ).fetchone()
    if not row_db:
        raise KeyError("event_server_id not found for zone_user_progress")
    return int(row_db[0])


def _resolve_event_uuid(row: dict, event_server_id: int) -> str:
    event_uuid = row.get("event_uuid")
    if event_uuid:
        return event_uuid
    return _to_uuid(event_server_id)


def _resolve_zone_uuid(row: dict) -> str:
    zone_uuid = row.get("zone_uuid")
    if zone_uuid:
        return zone_uuid
    zone_server_id = row.get("zone_server_id")
    if zone_server_id is None:
        raise KeyError("zone_uuid or zone_server_id required for zone_user_progress")
    return _to_uuid(zone_server_id)


def _resolve_user_uuid(row: dict) -> str:
    user_uuid = row.get("user_uuid")
    if user_uuid:
        return user_uuid
    user_server_id = row.get("user_server_id")
    if user_server_id is None:
        raise KeyError("user_uuid or user_server_id required for zone_user_progress")
    return _to_uuid(user_server_id)


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
            source,
            synced,
            synced_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            source=excluded.source,
            synced=excluded.synced,
            synced_at=excluded.synced_at
    """
    for r in rows:
        event_server_id = _resolve_event_server_id(conn, r)
        conn.execute(
            sql,
            (
                r["uuid"],
                r.get("server_id"),
                _resolve_event_uuid(r, event_server_id),
                event_server_id,
                _resolve_zone_uuid(r),
                r["zone_server_id"],
                _resolve_user_uuid(r),
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
                r.get("source", "mobile"),
                r.get("synced", 0),
                r.get("synced_at"),
            ),
        )
    conn.commit()
    conn.close()
