# backend/app/services/sync/pull_service.py

from datetime import datetime, timezone
from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser


async def pull_sync(since: datetime, user: CurrentUser) -> Dict[str, Any]:
    """
    Retorna alterações incrementais desde o timestamp `since`
    para a empresa do usuário autenticado.
    """

    sb = get_supabase_service_client()
    company_id = user.company_id

    def fetch_by_company(table: str):
        return (
            sb.table(table)
            .select("*")
            .eq("company_id", company_id)
            .gte("updated_at", since.isoformat())
            .execute()
            .data
            or []
        )

    def fetch_company():
        return (
            sb.table("companies")
            .select("*")
            .eq("id", company_id)
            .gte("updated_at", since.isoformat())
            .execute()
            .data
            or []
        )

    def fetch_zones():
        # 1️⃣ Buscar IDs dos eventos da empresa
        events_resp = (
            sb.table("inventory_events")
            .select("id")
            .eq("company_id", company_id)
            .execute()
        )

        event_rows = events_resp.data or []

        if not isinstance(event_rows, list) or not event_rows:
            return []

        event_ids = [
            row["id"]
            for row in event_rows
            if isinstance(row, dict) and "id" in row
        ]

        if not event_ids:
            return []

        # 2️⃣ Buscar zones associadas a esses eventos
        return (
            sb.table("zones")
            .select("*")
            .in_("event_id", event_ids)
            .gte("updated_at", since.isoformat())
            .execute()
            .data
            or []
        )

    def fetch_event_targets():
        return (
            sb.table("inventory_event_targets")
            .select("*")
            .eq("company_id", company_id)
            .gte("updated_at", since.isoformat())
            .execute()
            .data
            or []
        )

    def fetch_barcodes():
        return (
            sb.table("product_barcodes")
            .select("*")
            .eq("company_id", company_id)
            .gte("updated_at", since.isoformat())
            .execute()
            .data
            or []
        )

    return {
        "companies": fetch_company(),
        "users": fetch_by_company("users"),
        "locations": fetch_by_company("locations"),
        "product_categories": fetch_by_company("product_categories"),
        "products": fetch_by_company("products"),
        "product_barcodes": fetch_barcodes(),
        "inventory_events": fetch_by_company("inventory_events"),
        "inventory_event_targets": fetch_event_targets(),
        "zones": fetch_zones(),
        "server_ts": datetime.now(timezone.utc).isoformat(),
    }
