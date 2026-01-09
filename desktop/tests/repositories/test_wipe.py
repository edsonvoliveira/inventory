from desktop.bootstrap.bootstrap import bootstrap_app, wipe_local_database
from desktop.data.repositories.app_meta_repo import get_meta, set_meta
import os
from desktop.config.settings import DB_PATH

print("=== TESTE WIPE DB DESKTOP ===")

# Garante DB inicial
bootstrap_app()
set_meta("company_id", "1")
set_meta("bootstrap_done", "true")

print("Antes do wipe:")
print("DB existe?", os.path.exists(DB_PATH))
print("company_id =", get_meta("company_id"))
print("bootstrap_done =", get_meta("bootstrap_done"))

# Executa wipe
wipe_local_database()

print("\nDepois do wipe:")
print("DB existe?", os.path.exists(DB_PATH))
print("company_id =", get_meta("company_id"))
print("bootstrap_done =", get_meta("bootstrap_done"))
print("db_schema_version =", get_meta("db_schema_version"))
