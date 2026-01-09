# desktop/data/repositories/users_repo.py

from desktop.data.db.connection import get_connection
from datetime import datetime, timezone
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todos os usuários locais pelos dados vindos do servidor.
    Usado apenas em:
    - bootstrap inicial
    - full resync controlado
    """
    conn = get_connection()

    conn.execute("DELETE FROM users_local")

    now = datetime.now(timezone.utc).isoformat()

    for r in rows:
        conn.execute(
            """
            INSERT INTO users_local (
                uuid,
                server_id,
                email,
                name,
                role,
                company_id,
                last_sync_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["uuid"],
                r["id"],       # id do user no Postgres
                r["email"],
                r.get("name"),
                r["role"],
                r["company_id"],      # id da company no Postgres
                now,
            ),
        )

    conn.commit()
    conn.close()
