# desktop/utils/scripts/init_db_local.py

"""
Responsibilities:
- Utility helpers for init db local.
- Provide shared helper functions.
"""

#desktop/scripts/init_db_local.py

from desktop.data.db.connection import get_connection
from desktop.data.schema import SCHEMA_SQL

conn = get_connection()
conn.executescript(SCHEMA_SQL)
conn.commit()
conn.close()

print("DB local criado")