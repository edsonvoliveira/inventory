# backend/app/services/sync/handlers/product_barcodes.py

"""
Responsibilities:
- Sync handler for product barcodes entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/product_barcodes.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.services.sync.handlers._helpers import record_exists_by_uuid, should_apply_lww, resolve_fk_id
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class ProductBarcodeSyncHandler(BaseSyncHandler):
    table_name = "product_barcodes"

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
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()
        if record_exists_by_uuid(sb, self.table_name, record_uuid):
            return

        product_id = resolve_fk_id(
            sb,
            table_name="products",
            record_id=payload.get("product_id", payload.get("product_server_id")),
            record_uuid=payload.get("product_uuid"),
            company_id=user.company_server_id,
            require_active=True,
            field="product_id",
        )
        data = {
            "uuid": record_uuid,
            "company_id": user.company_server_id,
            "product_id": product_id,  # server_id do produto
            "barcode": payload["barcode"],
            "description": payload.get("description"),
            "is_active": payload.get("is_active", True),
        }

        sb.table("product_barcodes").insert(data).execute()

    # ---------------------------
    # PUSH (UPDATE)
    # ---------------------------
    def update(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()
        if not should_apply_lww(sb, self.table_name, record_uuid, payload.get("client_updated_at")):
            return

        self._reject_unknown_fields(payload, allowed_fields=[
            "barcode",
            "description",
            "is_active",
            "client_updated_at",
        ])

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

    # ---------------------------
    # PUSH (DELETE)
    # ---------------------------
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()

        sb.table("product_barcodes").update(
            {"is_active": False}
        ).eq(
            "uuid", record_uuid
        ).execute()
