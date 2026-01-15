# mobile/bootstrap/bootstrap.py

"""
Responsibilities:
- Initialize local database and schema.
- Provide bootstrap and reset helpers.
"""

# mobile/bootstrap/bootstrap.py
import os
from mobile.data.db.connection import get_connection
from mobile.data.db.schema import SCHEMA_SQL, SCHEMA_VERSION
from mobile.config.settings import DB_PATH
from mobile.data.repositories.app_meta_repo import set_meta

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
    Apaga completamente o DB Mobile e recria o schema.
    Usado quando:
    - troca de empresa
    - reset forçado
    - inconsistência local
    """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

    set_meta("db_schema_version", str(SCHEMA_VERSION))
    set_meta("bootstrap_done", "false")