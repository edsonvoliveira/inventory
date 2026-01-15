# mobile/data/migrations.py

"""
Responsibilities:
- Define database migrations.
- Apply schema upgrades for local storage.
"""

from typing import Callable


def ensure_meta_table(conn) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT)")


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


MIGRATIONS: dict[int, Callable] = {
    2: _migrate_to_2,
    3: _migrate_to_3,
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
