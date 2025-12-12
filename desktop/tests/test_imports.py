from config.settings import DB_PATH
from data.db.connection import get_connection

print("DB_PATH =", DB_PATH)
print("Connection OK =", get_connection())
