# desktop/data/repositories/inventory_events_repo.py
"""
Responsabilidade
- Inserir eventos de inventário
- Apenas estrutura do evento
- Zonas, targets e itens vêm depois
"""
from desktop.data.db.connection import get_connection
from typing import List, Dict, Any


def replace_all(rows: List[Dict[str, Any]]):
    """
    Substitui todos os eventos locais pelos dados vindos do servidor.
    Usado em:
    - bootstrap inicial
    - full resync
    """
    conn = get_connection()

    conn.execute("DELETE FROM inventory_events_local")

    for r in rows:
        conn.execute(
            """
            INSERT INTO inventory_events_local (
                uuid,
                server_id,
                title,
                status,
                event_type,
                synced
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["id"],
                r["title"],
                r["status"],
                r.get("event_type"),
            ),
        )

    conn.commit()
    conn.close()
