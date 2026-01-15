# desktop/tests/bootstrap/test_imports.py

"""
Responsibilities:
- Test imports behavior.
"""

from desktop.config.settings import DB_PATH
from desktop.data.db.connection import get_connection

print("DB_PATH =", DB_PATH)
print("Connection OK =", get_connection())
