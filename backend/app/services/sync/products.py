# backend/app/services/sync/products.py

from typing import Dict, Any
from app.services.sync.base import BaseSyncHandler
from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser


class ProductSyncHandler(BaseSyncHandler):
    table_name = "products"

    def insert(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: CurrentUser,
    ) -> None:
        sb = get_supabase_service_client()

        sb.table("products").insert({
            "uuid": record_uuid,
            "company_id": payload["company_id"],
            "sku": payload["sku"],
            "name": payload["name"],
            "uom_inventory": payload["uom_inventory"],
            "is_active": payload.get("is_active", True),
        }).execute()

    def update(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: CurrentUser,
    ) -> None:
        sb = get_supabase_service_client()

        sb.table("products").update(payload).eq(
            "uuid", record_uuid
        ).execute()

    def delete(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: CurrentUser,
    ) -> None:
        sb = get_supabase_service_client()

        sb.table("products").update({
            "is_active": False
        }).eq("uuid", record_uuid).execute()
