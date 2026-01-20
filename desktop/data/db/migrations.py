# desktop/data/db/migrations.py

"""
Responsibilities:
- Define database migrations.
- Apply schema upgrades for local storage.
"""

def _column_exists(conn, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)


def run_migrations_if_needed(conn) -> None:
    """
    Apply small schema fixes for existing DBs.
    """
    if not _column_exists(conn, "inventory_events_local", "status"):
        conn.execute(
            "ALTER TABLE inventory_events_local ADD COLUMN status TEXT NOT NULL DEFAULT 'planned'"
        )
    if not _column_exists(conn, "zones_local", "count_status"):
        conn.execute(
            "ALTER TABLE zones_local ADD COLUMN count_status TEXT NOT NULL DEFAULT 'not_started'"
        )
