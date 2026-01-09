import os
from desktop.data.db.schema import SCHEMA_SQL, SCHEMA_VERSION
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import set_meta, get_meta

DB_PATH = "desktop/data/db/app.db"

def recreate_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

def ensure_schema():
    current = get_meta("schema_version")

    if current != str(SCHEMA_VERSION):
        recreate_database()
        set_meta("schema_version", str(SCHEMA_VERSION))
