# desktop/core/bootstrap_service.py

from datetime import datetime, timezone

from desktop.core.http_client import get
from desktop.config.settings import SYNC_BOOTSTRAP_ENDPOINT
from desktop.data.repositories import (
    app_meta_repo,
    companies_repo,
    users_repo,
    locations_repo,
    product_categories_repo,
    products_repo,
    product_barcodes_repo,
    inventory_events_repo,
    inventory_event_targets_repo,
    zones_repo,
)


def run_bootstrap(jwt_token: str) -> bool:
    """
    Executa o bootstrap real do Desktop:
    - chama o DV Server
    - popula todas as tabelas locais
    - grava metadados de estado
    """

    payload = get(SYNC_BOOTSTRAP_ENDPOINT, jwt_token)

    # --- Persistência local (ordem importa) ---
    companies_repo.replace_all([payload["company"]])
    users_repo.replace_all(payload.get("users", []))
    locations_repo.replace_all(payload.get("locations", []))
    product_categories_repo.replace_all(payload.get("product_categories", []))
    products_repo.replace.all(payload.get("products", []))
    product_barcodes_repo.replace_all(payload.get("product_barcodes", []))
    inventory_events_repo.replace_all(payload.get("inventory_events", []))
    inventory_event_targets_repo.replace_all(payload.get("inventory_event_targets", []))
    zones_repo.replace_all(payload.get("zones", []))

    # --- Metadados ---
    app_meta_repo.set_meta("bootstrap_done", "true")
    app_meta_repo.set_meta(
        "last_full_sync_at",
        datetime.now(timezone.utc).isoformat(),
    )

    return True
