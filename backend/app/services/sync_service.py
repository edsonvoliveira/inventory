from datetime import datetime, timezone
from typing import Any, Dict, List, cast

from app.clients.supabase_client import get_supabase_service_client


async def bootstrap_sync(user):
    sb = get_supabase_service_client()

    def fetch(table: str) -> List[Dict[str, Any]]:
        resp = sb.table(table).select("*").execute()
        if not resp.data:
            return []
        return cast(List[Dict[str, Any]], resp.data)

    companies = fetch("companies")
    if not companies:
        raise RuntimeError("Empresa não encontrada para o usuário autenticado")

    return {
        "company": companies[0],
        "users": fetch("users"),
        "locations": fetch("locations"),
        "products": fetch("products"),
        "product_barcodes": fetch("product_barcodes"),
        "inventory_events": fetch("inventory_events"),
        "inventory_event_targets": fetch("inventory_event_targets"),
        "zones": fetch("zones"),
        "server_ts": datetime.now(timezone.utc).isoformat(),
    }
