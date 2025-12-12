# mobile/data/db/connection.py
import sqlite3
from mobile.config.settings import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)
