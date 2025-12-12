# data/repositories/app_meta_repo.py
"""
Responsabilidade:
- Ler/escrever app_meta
- Funções simples (get, set, delete, clear)
"""

from desktop.data.db.connection import get_connection

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
