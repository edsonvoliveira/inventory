#desktop/tests/helpers/db.py

"""
Responsabilities:
- Helpers for database testing
- Setup and teardown of test database
- Utility functions for inserting and querying test data
- Designed to facilitate unit and integration tests
"""

import sqlite3
from desktop.data.db.schema import SCHEMA_SQL

def make_test_connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_SQL)
    return conn