# backend/app/services/sync/products.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class ProductSyncHandler(BaseSyncHandler):
    table_name = "products"

    # --------------------------------------------------
    # INSERT
    # --------------------------------------------------
    def insert(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: CurrentUser,
    ) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "company_id": payload["company_id"],
            "sku": payload["sku"],
            "name": payload["name"],
            "description": payload.get("description"),
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

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: CurrentUser,
    ) -> None:
        sb = get_supabase_service_client()

        update_data = {}

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
            raise RuntimeError("Nenhum campo válido para update de product")

        sb.table("products").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    def delete(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: CurrentUser,
    ) -> None:
        sb = get_supabase_service_client()

        sb.table("products").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
