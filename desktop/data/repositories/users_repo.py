# desktop/data/repositories/users_repo.py

from desktop.data.db.connection import get_connection


def replace_all(rows: list[dict]):
    conn = get_connection()
    conn.execute("DELETE FROM users_local")

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
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                r["uuid"],        # UUID do Supabase
                r["id"],          # server_id ← id do Supabase
                r["email"],
                r.get("name"),
                r["role"],
                r["company_id"],  # ID da empresa no servidor
            ),
        )

    conn.commit()
    conn.close()
