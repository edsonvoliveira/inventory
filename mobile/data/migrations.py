# mobile/data/migrations.py

"""
Responsibilities:
- Define database migrations.
- Apply schema upgrades for local storage.
"""

from typing import Callable


def ensure_meta_table(conn) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT)")

def _column_exists(conn, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)


def get_schema_version(conn) -> int:
    ensure_meta_table(conn)
    cur = conn.execute("SELECT value FROM app_meta WHERE key = ?", ("schema_version",))
    row = cur.fetchone()
    return int(row[0]) if row and str(row[0]).isdigit() else 0


def set_schema_version(conn, version: int) -> None:
    conn.execute(
        "INSERT INTO app_meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        ("schema_version", str(version)),
    )


def _migrate_to_2(conn) -> None:
    # Placeholder for legacy migration logic.
    # Keep empty for now; reset flow handles incompatibilities.
    return None


def _migrate_to_3(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS product_categories_local (
          uuid TEXT PRIMARY KEY,
          server_id INTEGER NOT NULL UNIQUE,

          company_server_id INTEGER NOT NULL,

          code TEXT,
          name TEXT NOT NULL,
          description TEXT,

          is_active INTEGER DEFAULT 1,

          updated_at TEXT,
          deleted_at TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_product_categories_local_company_server_id ON product_categories_local(company_server_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_product_categories_local_name ON product_categories_local(name)"
    )


def _migrate_to_4(conn) -> None:
    conn.execute("ALTER TABLE outbox_local ADD COLUMN status TEXT DEFAULT 'pending'")
    conn.execute("ALTER TABLE outbox_local ADD COLUMN max_attempts INTEGER DEFAULT 5")
    conn.execute(
        "UPDATE outbox_local SET status = 'pending' WHERE status IS NULL OR status = ''"
    )


def _migrate_to_5(conn) -> None:
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_companies_local_updated_at ON companies_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_users_local_updated_at ON users_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_devices_local_updated_at ON devices_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_locations_local_updated_at ON locations_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_events_local_updated_at ON inventory_events_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_zones_local_updated_at ON zones_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_targets_local_updated_at ON inventory_event_targets_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_product_categories_local_updated_at ON product_categories_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_local_updated_at ON products_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_barcodes_local_updated_at ON product_barcodes_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_items_local_updated_at ON inventory_items_local(updated_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_progress_local_updated_at ON zone_user_progress_local(updated_at)"
    )


def _migrate_to_6(conn) -> None:
    conn.execute(
        "UPDATE inventory_events_local SET required_counts = 1 WHERE required_counts IS NULL"
    )
    conn.execute(
        "UPDATE zones_local SET count_status = 'not_started' WHERE count_status IS NULL"
    )
    conn.execute(
        "UPDATE inventory_event_targets_local SET expected_qty = 0 WHERE expected_qty IS NULL"
    )

def _migrate_to_7(conn) -> None:
    if not _column_exists(conn, "inventory_events_local", "status"):
        conn.execute(
            "ALTER TABLE inventory_events_local ADD COLUMN status TEXT NOT NULL DEFAULT 'planned'"
        )
    if not _column_exists(conn, "zones_local", "count_status"):
        conn.execute(
            "ALTER TABLE zones_local ADD COLUMN count_status TEXT NOT NULL DEFAULT 'not_started'"
        )


MIGRATIONS: dict[int, Callable] = {
    2: _migrate_to_2,
    3: _migrate_to_3,
    4: _migrate_to_4,
    5: _migrate_to_5,
    6: _migrate_to_6,
    7: _migrate_to_7,
}


def migrate_schema(conn, current: int, target: int) -> None:
    if current >= target:
        return
    for version in range(current + 1, target + 1):
        migration = MIGRATIONS.get(version)
        if migration is None:
            raise RuntimeError(f"Missing migration for version {version}")
        migration(conn)
        set_schema_version(conn, version)
