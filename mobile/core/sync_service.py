# mobile/core/sync_service.py

"""
Responsibilities:
- Service layer for sync workflows.
- Coordinate related operations and dependencies.
"""

# mobile/core/sync_service.py
from datetime import datetime

from mobile.bootstrap.bootstrap import wipe_local_database
from mobile.data.repositories.app_meta_repo import get_meta, set_meta
from mobile.data.repositories import (
    companies_repo,
    users_repo,
    products_repo,
    product_barcodes_repo,
    events_repo,
    event_targets_repo,
    zones_repo,
)

# -------------------------------------------------
# BOOTSTRAP LÓGICO (APÓS LOGIN)
# -------------------------------------------------

def ensure_bootstrap_for_company(
    company_id: int,
    company_uuid: str
) -> bool:
    """
    Garante que o DB Mobile está inicializado para a empresa correta.
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

    return False


def _prepare_bootstrap(company_id: int, company_uuid: str):
    set_meta("company_id", str(company_id))
    set_meta("company_uuid", company_uuid)
    set_meta("bootstrap_done", "false")


# -------------------------------------------------
# FULL SYNC (SIMULADO)
# -------------------------------------------------

def run_full_sync():
    """
    Simula o endpoint /sync/bootstrap para Mobile.
    """
    payload = _mock_bootstrap_payload()

    companies_repo.replace_all(payload["companies"])
    users_repo.replace_all(payload["users"])
    products_repo.replace_all(payload["products"])
    product_barcodes_repo.replace_all(payload["barcodes"])
    events_repo.replace_all(payload["events"])
    event_targets_repo.replace_all(payload["targets"])
    zones_repo.replace_all(payload["zones"])

    now = datetime.utcnow().isoformat()
    set_meta("last_full_sync_at", now)
    set_meta("last_incremental_sync_at", now)
    set_meta("bootstrap_done", "true")


# -------------------------------------------------
# MOCK DO SERVIDOR
# -------------------------------------------------

def _mock_bootstrap_payload():
    return {
        "companies": [
            {
                "uuid": "company-uuid-1",
                "server_id": 1,
                "name": "Empresa Demo",
            }
        ],
        "users": [
            {
                "uuid": "user-uuid-1",
                "server_id": 1,
                "name": "Operador",
                "role": "counter",
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
        "barcodes": [
            {
                "uuid": "bc-uuid-1",
                "server_id": 1,
                "product_uuid": "prod-uuid-1",
                "barcode": "560000000001",
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
        "targets": [
            {
                "uuid": "target-uuid-1",
                "server_id": 1,
                "event_uuid": "event-uuid-1",
                "product_uuid": "prod-uuid-1",
                "expected_qty": 100,
            }
        ],
        "zones": [
            {
                "uuid": "zone-uuid-1",
                "server_id": 1,
                "event_uuid": "event-uuid-1",
                "name": "Zona A",
                "count_status": "open",
                "lock_status": "unlocked",
            }
        ],
    }
