# backend/app/services/sync/handlers/products.py

"""
Responsibilities:
- Sync handler for products entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/products.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class ProductSyncHandler(BaseSyncHandler):
    table_name = "products"

    # ---------------------------
    # PULL
    # ---------------------------
    def pull(
        self,
        *,
        company_id: int,
        since: Optional[datetime],
    ) -> List[Dict[str, Any]]:

        sb = get_supabase_service_client()

        query = (
            sb.table(self.table_name)
            .select("*")
            .eq("company_id", company_id)
        )

        if since is not None:
            query = query.gte("updated_at", since.astimezone(timezone.utc).isoformat())

        result = query.execute()
        data = result.data or []

        out: List[Dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                out.append(item)
            else:
                # se vier algo inesperado, ignore ou levante erro
                # raise TypeError(f"Unexpected item type: {type(item)}")
                continue
        return out

    # ---------------------------
    # PUSH (INSERT)
    # ---------------------------
    def insert(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        sb = get_supabase_service_client()

        category_id = payload.get("category_id", payload.get("category_server_id"))
        if category_id == "":
            category_id = None

        data = {
            "uuid": record_uuid,
            "company_id": user.company_server_id,
            "sku": payload["sku"],
            "name": payload["name"],
            "description": payload.get("description"),
            "category_id": category_id,
            "uom_base": payload["uom_base"],
            "uom_inventory": payload["uom_inventory"],
            "conversion_factor": payload.get("conversion_factor", 1),
            "system_qty": payload.get("system_qty", 0),
            "cost_price": payload.get("cost_price"),
            "is_sensitive": payload.get("is_sensitive", False),
            "serial_number_enabled": payload.get("serial_number_enabled", False),
            "is_active": True,
        }

        sb.table("products").insert(data).execute()

    # ---------------------------
    # PUSH (UPDATE)
    # ---------------------------
    def update(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        sb = get_supabase_service_client()

        update_data = {}

        category_id = payload.get("category_id", payload.get("category_server_id"))
        if category_id is not None and category_id != "":
            update_data["category_id"] = category_id

        allowed_fields = [
            "sku",
            "name",
            "description",
            "uom_base",
            "uom_inventory",
            "conversion_factor",
            "system_qty",
            "cost_price",
            "is_sensitive",
            "serial_number_enabled",
            "is_active",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo valido para update de product")

        sb.table("products").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ---------------------------
    # PUSH (DELETE)
    # ---------------------------
    def delete(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        sb = get_supabase_service_client()

        sb.table("products").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
