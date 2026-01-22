# mobile/data/db/connection.py

"""
Responsibilities:
- Create and return database connections.
- Centralize DB connection handling.
"""

# mobile/data/db/connection.py
import sqlite3
from mobile.config.settings import DB_PATH

_BUSY_TIMEOUT_MS = 5000


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=_BUSY_TIMEOUT_MS / 1000.0,
        check_same_thread=False,
    )
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute(f"PRAGMA busy_timeout={_BUSY_TIMEOUT_MS}")
    return conn
