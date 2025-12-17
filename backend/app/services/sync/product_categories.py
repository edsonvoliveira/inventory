# backend/app/services/sync/product_categories.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class ProductCategorySyncHandler(BaseSyncHandler):
    table_name = "product_categories"

    # --------------------------------------------------
    # INSERT
    # --------------------------------------------------
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "company_id": payload["company_id"],
            "code": payload["code"],
            "name": payload["name"],
            "description": payload.get("description"),
            "is_active": True,
        }

        sb.table("product_categories").insert(data).execute()

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        update_data: Dict[str, Any] = {}

        allowed_fields = [
            "code",
            "name",
            "description",
            "is_active",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de product_category")

        sb.table("product_categories").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # --------------------------------------------------
    # SOFT DELETE
    # --------------------------------------------------
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        sb.table("product_categories").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
