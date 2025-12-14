from desktop.core.http_client import get
from desktop.config.settings import SYNC_BOOTSTRAP_ENDPOINT
from desktop.data.repositories.app_meta_repo import set_meta

from desktop.data.repositories.companies_repo import replace_all as replace_companies
from desktop.data.repositories.users_repo import replace_all as replace_users
from desktop.data.repositories.products_repo import replace_all as replace_products
from desktop.data.repositories.events_repo import replace_all as replace_events


def run_bootstrap(token: str) -> bool:
    """
    Executa o bootstrap inicial do Desktop:
    - Chama o DV Server
    - Substitui dados locais (full sync)
    - Atualiza app_meta
    """

    payload = get(SYNC_BOOTSTRAP_ENDPOINT, token)

    # -----------------------------
    # Persistência (FULL REPLACE)
    # -----------------------------
    replace_companies([payload["company"]])
    replace_users(payload["users"])
    replace_products(payload["products"])
    replace_events(payload["inventory_events"])

    # -----------------------------
    # Metadados do app
    # -----------------------------
    set_meta("bootstrap_done", "true")
    set_meta("last_full_sync_at", payload["server_ts"])

    return True
