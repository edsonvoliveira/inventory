# mobile/data/repositories/app_meta_repo.py

"""
Responsibilities:
- Repository for app meta data.
- Define persistence and sync behavior.
"""

# mobile/data/repositories/app_meta_repo.py
from mobile.data.db.connection import get_connection

def get_meta(key: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM app_meta WHERE key = ?",
        (key,)
    ).fetchone()
    conn.close()
    return row[0] if row else None

def set_meta(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO app_meta (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()
