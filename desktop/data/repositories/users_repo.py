"""
Responsabilidade
- Limpar users_local
- Inserir usuários vindos do servidor
- Nenhuma lógica de permissão
- Nenhuma lógica de sessão
"""

from desktop.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    """
    Substitui completamente os usuários locais
    (usado apenas no bootstrap lógico).
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users_local")

    for r in rows:
        cur.execute(
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
            VALUES (?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                r["uuid"],
                r["server_id"],
                r["email"],
                r.get("name"),
                r["role"],
                r["company_id"],
            ),
        )

    conn.commit()
    conn.close()
