# mobile/data/repositories/events_repo.py

"""
Responsibilities:
- Repository for events data.
- Define persistence and sync behavior.
"""

from mobile.data.db.connection import get_connection


def replace_all(rows: list[dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory_events_local")
    for r in rows:
        cur.execute(
            """
            INSERT INTO inventory_events_local (
                uuid,
                server_id,
                company_server_id,
                location_server_id,
                title,
                event_type,
                status,
                required_counts,
                required_audits,
                tolerance_percent,
                tolerance_absolute,
                primary_finished_at,
                audit_finished_at,
                is_active,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["company_server_id"],
                r["location_server_id"],
                r["title"],
                r.get("event_type"),
                r["status"],
                r.get("required_counts", 1),
                r.get("required_audits"),
                r.get("tolerance_percent"),
                r.get("tolerance_absolute"),
                r.get("primary_finished_at"),
                r.get("audit_finished_at"),
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
        INSERT INTO inventory_events_local (
            uuid,
            server_id,
            company_server_id,
            location_server_id,
            title,
            event_type,
            status,
            required_counts,
            required_audits,
            tolerance_percent,
            tolerance_absolute,
            primary_finished_at,
            audit_finished_at,
            is_active,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            uuid=excluded.uuid,
            server_id=excluded.server_id,
            company_server_id=excluded.company_server_id,
            location_server_id=excluded.location_server_id,
            title=excluded.title,
            event_type=excluded.event_type,
            status=excluded.status,
            required_counts=excluded.required_counts,
            required_audits=excluded.required_audits,
            tolerance_percent=excluded.tolerance_percent,
            tolerance_absolute=excluded.tolerance_absolute,
            primary_finished_at=excluded.primary_finished_at,
            audit_finished_at=excluded.audit_finished_at,
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
                r["location_server_id"],
                r["title"],
                r.get("event_type"),
                r["status"],
                r.get("required_counts", 1),
                r.get("required_audits"),
                r.get("tolerance_percent"),
                r.get("tolerance_absolute"),
                r.get("primary_finished_at"),
                r.get("audit_finished_at"),
                r.get("is_active", 1),
                r.get("updated_at"),
            ),
        )
    conn.commit()
    conn.close()
