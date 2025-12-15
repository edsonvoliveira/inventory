# desktop/data/repositories/locations_repo.py

from desktop.data.db.connection import get_connection
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todos os locais locais pelos dados vindos do servidor.
    Usado apenas em:
    - bootstrap inicial
    - full resync controlado
    """
    conn = get_connection()

    conn.execute("DELETE FROM locations_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO locations_local (
                uuid,
                server_id,
                code,
                name,
                is_active,
                synced
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["server_id"],          # id do location no Postgres
                r.get("code"),
                r["name"],
                1 if r.get("is_active", True) else 0,
            ),
        )

    conn.commit()
    conn.close()
