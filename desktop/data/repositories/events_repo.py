"""
Responsabilidade
- Inserir eventos de inventário
- Apenas estrutura do evento
- Zonas, targets e itens vêm depois
"""

from desktop.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    """
    Substitui completamente os eventos locais
    (bootstrap lógico).
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM inventory_events_local")

    for r in rows:
        cur.execute(
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
