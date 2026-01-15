# desktop/tests/bootstrap/test_bootstrap.py

"""
Responsibilities:
- Test bootstrap behavior.
"""

from desktop.bootstrap.bootstrap import bootstrap_app
from desktop.data.repositories.app_meta_repo import get_meta
import os
from desktop.config.settings import DB_PATH

# Apagar DB se existir (simular primeira execução)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("DB existente antes do bootstrap?", os.path.exists(DB_PATH))

bootstrap_app()

print("DB existente depois do bootstrap?", os.path.exists(DB_PATH))
print("db_schema_version =", get_meta("db_schema_version"))
print("bootstrap_done =", get_meta("bootstrap_done"))
