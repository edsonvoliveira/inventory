# desktop/data/db/connection.py

"""
Responsibilities:
- Create and return database connections.
- Centralize DB connection handling.
"""

import sqlite3
from desktop.config.settings import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)
