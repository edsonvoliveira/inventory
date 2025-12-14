"""
Responsabilidade
- Substituir completamente o catálogo local
- Trabalhar apenas com dados mestre
- Nenhuma regra de inventário
"""

from desktop.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    """
    Substitui completamente os produtos locais
    (bootstrap lógico).
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM products_local")

    for r in rows:
        cur.execute(
            """
            INSERT INTO products_local (
                uuid,
                server_id,
                sku,
                name,
                is_active,
                synced
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                r["uuid"],
                r["id"],
                r["sku"],
                r["name"],
                r.get("is_active", 1),
            ),
        )

    conn.commit()
    conn.close()
