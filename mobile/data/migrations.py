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


MIGRATIONS: dict[int, Callable] = {
    2: _migrate_to_2,
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
