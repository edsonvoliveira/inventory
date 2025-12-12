# data/db/connection.py

""""
Responsabilidade:
    Definir onde fica o SQLite
    Criar conexões
"""

import sqlite3
from desktop.config.settings import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)
