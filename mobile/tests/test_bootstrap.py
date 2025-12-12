from mobile.bootstrap.bootstrap import bootstrap_app
from mobile.data.repositories.app_meta_repo import get_meta
from mobile.config.settings import DB_PATH
import os

print("=== TESTE BOOTSTRAP MOBILE ===")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("DB existe antes?", os.path.exists(DB_PATH))

bootstrap_app()

print("DB existe depois?", os.path.exists(DB_PATH))
print("db_schema_version =", get_meta("db_schema_version"))
print("bootstrap_done =", get_meta("bootstrap_done"))
