# desktop/core/sync_service.py
from datetime import datetime

from desktop.bootstrap.bootstrap import wipe_local_database
from desktop.data.repositories.app_meta_repo import (
    get_meta,
    set_meta,
)
from desktop.data.repositories import (
    companies_repo,
    users_repo,
    products_repo,
    events_repo,
)

# -------------------------------------------------
# BOOTSTRAP LÓGICO (APÓS LOGIN)
# -------------------------------------------------

def ensure_bootstrap_for_company(
    company_id: int,
    company_uuid: str
) -> bool:
    """
    Garante que o DB local está inicializado para a empresa correta.
    Retorna True se o bootstrap foi executado.
    """

    stored_company_id = get_meta("company_id")
    bootstrap_done = get_meta("bootstrap_done") == "true"

    # DB nunca inicializado
    if stored_company_id is None:
        _prepare_bootstrap(company_id, company_uuid)
        run_full_sync()
        return True

    # Empresa diferente → reset total
    if stored_company_id != str(company_id):
        wipe_local_database()
        _prepare_bootstrap(company_id, company_uuid)
        run_full_sync()
        return True

    # Mesma empresa, mas bootstrap incompleto
    if not bootstrap_done:
        run_full_sync()
        return True

    # Tudo OK
    return False


def _prepare_bootstrap(company_id: int, company_uuid: str):
    """
    Prepara o app_meta para bootstrap lógico.
    """
    set_meta("company_id", str(company_id))
    set_meta("company_uuid", company_uuid)
    set_meta("bootstrap_done", "false")


# -------------------------------------------------
# FULL SYNC (SIMULADO)
# -------------------------------------------------

def run_full_sync():
    """
    Simula o endpoint /sync/bootstrap do DV Server.
    """

    payload = _mock_bootstrap_payload()

    # Grava dados mestre
    companies_repo.replace_all(payload["companies"])
    users_repo.replace_all(payload["users"])
    products_repo.replace_all(payload["products"])
    events_repo.replace_all(payload["events"])

    # Marca bootstrap como concluído
    now = datetime.utcnow().isoformat()
    set_meta("last_full_sync_at", now)
    set_meta("last_incremental_sync_at", now)
    set_meta("bootstrap_done", "true")


# -------------------------------------------------
# MOCK DO SERVIDOR
# -------------------------------------------------

def _mock_bootstrap_payload():
    """
    Simula resposta do DV Server para bootstrap inicial.
    """

    return {
        "companies": [
            {
                "uuid": "company-uuid-1",
                "server_id": 1,
                "name": "Empresa Demo",
                "vat_number": "PT123456789",
                "is_active": 1,
            }
        ],
        "users": [
            {
                "uuid": "user-uuid-1",
                "server_id": 1,
                "email": "admin@empresa.demo",
                "name": "Admin",
                "role": "admin",
                "company_id": 1,
            }
        ],
        "products": [
            {
                "uuid": "prod-uuid-1",
                "server_id": 1,
                "sku": "SKU001",
                "name": "Produto Demo",
                "is_active": 1,
            }
        ],
        "events": [
            {
                "uuid": "event-uuid-1",
                "server_id": 1,
                "title": "Inventário Geral",
                "status": "open",
            }
        ],
    }
