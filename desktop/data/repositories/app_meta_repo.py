# desktop/data/repositories/app_meta_repo.py

"""
Responsibilities:
- Repository for app meta data.
- Define persistence and sync behavior.
"""

from desktop.data.db.connection import get_connection
from typing import Optional

def get_meta(key: str, conn=None) -> Optional[str]:
    owns = conn is None
    conn = conn or get_connection()

    row = conn.execute(
        "SELECT value FROM app_meta WHERE key = ?",
        (key,),
    ).fetchone()

    if owns:
        conn.close()

    return row[0] if row else None

def set_meta(key: str, value: str, conn=None) -> None:
    owns = conn is None
    conn = conn or get_connection()

    conn.execute(
        """
        INSERT INTO app_meta (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )
    conn.commit()

    if owns:
        conn.close()

def delete_meta(key: str):
    conn = get_connection()
    conn.execute("DELETE FROM app_meta WHERE key = ?", (key,))
    conn.commit()
    conn.close()

def clear_meta():
    conn = get_connection()
    conn.execute("DELETE FROM app_meta")
    conn.commit()
    conn.close()
