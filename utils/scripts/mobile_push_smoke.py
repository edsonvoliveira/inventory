# mobile_push_smoke.py

import os
from datetime import datetime, timezone

from mobile.app_core_container import build_services
from mobile.data.db.connection import get_connection
from mobile.data.queries import add_local_inventory_item, reset_db
from mobile.data.repositories.app_meta_repo import get_meta, set_meta


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Env {name} nao definido.")
    return value


def main() -> None:
    base_url = _require_env("DV_SERVER_BASE_URL")
    jwt_token = _require_env("E2E_JWT_TOKEN")
    company_id = int(_require_env("E2E_COMPANY_SERVER_ID"))
    company_uuid = os.getenv("E2E_COMPANY_UUID", f"server:{company_id}")

    reset_db()
    set_meta("dv_server_base_url", base_url)
    set_meta("jwt_token", jwt_token)
    set_meta("company_id", str(company_id))
    set_meta("company_uuid", company_uuid)
    set_meta("company_server_id", str(company_id))
    set_meta("bootstrap_done", "false")

    build_services().bootstrap.run()
    last_sync = get_meta(f"last_server_sync_at:{company_id}") or get_meta("last_pull_at")
    if not last_sync:
        raise SystemExit("Bootstrap executado, mas last_server_sync_at vazio.")

    conn = get_connection()
    zone = conn.execute(
        "SELECT server_id, event_server_id FROM zones_local LIMIT 1"
    ).fetchone()
    user = conn.execute("SELECT server_id FROM users_local LIMIT 1").fetchone()
    product = conn.execute("SELECT server_id FROM products_local LIMIT 1").fetchone()
    conn.close()

    if not zone or not user:
        raise SystemExit("Sem dados locais apos bootstrap.")

    zone_server_id, event_server_id = zone
    product_server_id = product[0] if product else None

    add_local_inventory_item(
        zone_id=zone_server_id,
        event_id=event_server_id,
        username="e2e",
        scanned_code="E2E-TEST",
        product_id=product_server_id,
        qty_counted=1,
    )

    conn = get_connection()
    record_uuid = conn.execute(
        "SELECT uuid FROM inventory_items_local ORDER BY created_at DESC LIMIT 1"
    ).fetchone()[0]
    conn.close()

    accepted, failed = build_services().sync_push.run()
    print(f"push accepted={accepted} failed={failed}")

    build_services().sync_pull.run()

    print("E2E mobile sync completo.")


if __name__ == "__main__":
    main()
