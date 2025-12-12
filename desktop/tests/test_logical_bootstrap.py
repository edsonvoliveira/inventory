from desktop.bootstrap.bootstrap import bootstrap_app
from desktop.core.sync_service import ensure_bootstrap_for_company
from desktop.data.repositories.app_meta_repo import get_meta
from desktop.config.settings import DB_PATH
import os

print("=== TESTE BOOTSTRAP LÓGICO ===")

# Garantir DB limpo
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

bootstrap_app()

executed = ensure_bootstrap_for_company(
    company_id=1,
    company_uuid="company-uuid-1"
)

print("Bootstrap executado?", executed)
print("company_id =", get_meta("company_id"))
print("bootstrap_done =", get_meta("bootstrap_done"))
print("last_full_sync_at =", get_meta("last_full_sync_at"))
