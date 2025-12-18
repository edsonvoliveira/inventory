# backend/app/services/sync/product_barcodes.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.core.security import CurrentUser
from app.services.sync.base import BaseSyncHandler


class ProductBarcodeSyncHandler(BaseSyncHandler):
    table_name = "product_barcodes"

    # ======================================================
    # INSERT
    # ======================================================
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        data = {
            "uuid": record_uuid,
            "company_id": user.company_id,
            "product_id": payload["product_id"],  # server_id do produto
            "barcode": payload["barcode"],
            "description": payload.get("description"),
            "is_active": payload.get("is_active", True),
        }

        sb.table("product_barcodes").insert(data).execute()

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        update_data = {}

        allowed_fields = [
            "barcode",
            "description",
            "is_active",
        ]

        for field in allowed_fields:
            if field in payload:
                update_data[field] = payload[field]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update de product_barcodes")

        sb.table("product_barcodes").update(update_data).eq(
            "uuid", record_uuid
        ).execute()

    # ======================================================
    # SOFT DELETE
    # ======================================================
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        sb.table("product_barcodes").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
