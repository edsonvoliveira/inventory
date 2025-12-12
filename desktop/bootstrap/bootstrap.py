# bootstrap/bootstrap.py
"""
Responsabilidade:
- Criar DB se não existir
- Aplicar schema.py
- Inicializar app_meta mínimo
- Nada de sync
- Nada de UI
"""

import os
from desktop.data.db.connection import get_connection
from desktop.data.db.schema import SCHEMA_SQL, SCHEMA_VERSION
from desktop.data.repositories.app_meta_repo import set_meta
from desktop.config.settings import DB_PATH

def bootstrap_app():
    first_run = not os.path.exists(DB_PATH)
    conn = get_connection()

    if first_run:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        set_meta("db_schema_version", str(SCHEMA_VERSION))
        set_meta("bootstrap_done", "false")

    conn.close()
    
def wipe_local_database():
    """
    Apaga completamente o banco local e recria o schema.
    Usado quando:
    - login de outra empresa
    - reset forçado
    - corrupção de dados
    """
    # Fecha qualquer conexão aberta implicitamente
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Recria DB limpo
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

    # Reinicializa meta
    set_meta("db_schema_version", str(SCHEMA_VERSION))
    set_meta("bootstrap_done", "false")