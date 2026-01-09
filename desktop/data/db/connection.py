# data/db/connection.py

""""
Responsabilities:
- Provide a connection to the local SQLite database
- Use DB_PATH from settings
- Encapsulate connection logic for reuse
"""

import sqlite3
from desktop.config.settings import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)
