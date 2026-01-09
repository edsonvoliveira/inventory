#desktop/scripts/init_db_local.py

from desktop.data.db.connection import get_connection
from desktop.data.db.schema import SCHEMA_SQL, SCHEMA_VERSION

conn = get_connection()
conn.executescript(SCHEMA_SQL)
conn.commit()
conn.close()

print(f"DB local criado com schema_version={SCHEMA_VERSION}")