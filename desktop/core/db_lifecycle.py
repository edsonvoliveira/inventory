#desktop/core/db_lifecycle.py

"""
Responsabilities:
- Manage database lifecycle
- Handle schema creation and updates
- Ensure database integrity
"""

import os

from desktop.data.db.schema import SCHEMA_SQL, SCHEMA_VERSION
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import set_meta, get_meta


def recreate_database() -> None:
    """
    Recria o DB local do zero (MVP: estratégia de reset completo).
    """
    conn = get_connection()

    # Descobre o path real do DB a partir da própria conexão (evita divergência)
    db_path = conn.execute("PRAGMA database_list").fetchone()[2]
    conn.close()

    if db_path and db_path != ":memory:" and os.path.exists(db_path):
        os.remove(db_path)

    conn = get_connection()
    try:
        conn.executescript(SCHEMA_SQL)
        set_meta("schema_version", str(SCHEMA_VERSION), conn)
        # Opcional, mas recomendado: resetar flags administrativas
        set_meta("bootstrap_done", "", conn)
        set_meta("last_pull_at", "", conn)
        conn.commit()
    finally:
        conn.close()


def ensure_schema() -> None:
    """
    Garante que o schema local esteja na versão esperada.
    Estratégia MVP: reset completo quando divergir.
    """
    conn = get_connection()
    try:
        current = get_meta("schema_version", conn)
        if current != str(SCHEMA_VERSION):
            conn.close()  # fecha antes de recriar (Windows/locks)
            recreate_database()
    finally:
        try:
            conn.close()
        except Exception:
            pass