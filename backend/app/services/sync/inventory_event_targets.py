# backend/app/services/sync/inventory_event_targets.py

from typing import Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.services.sync.base import BaseSyncHandler
from app.core.security import CurrentUser


class InventoryEventTargetSyncHandler(BaseSyncHandler):
    table_name = "inventory_event_targets"

    # --------------------------------------------------
    # Helpers (normalização para Pylance + robustez)
    # --------------------------------------------------
    def _first_row_as_dict(self, resp, err_msg: str) -> Dict[str, Any]:
        """
        Converte resp.data (List[JSON] | None) em Dict[str, Any] com validações.
        Evita warnings do Pylance e erros de runtime.
        """
        data = getattr(resp, "data", None)

        if not isinstance(data, list) or len(data) == 0:
            raise RuntimeError(err_msg)

        row = data[0]
        if not isinstance(row, dict):
            raise RuntimeError(err_msg)

        return row

    def _row_id_as_int(self, row: Dict[str, Any], err_msg: str) -> int:
        raw_id = row.get("id")
        if not isinstance(raw_id, (int, str)):
            raise RuntimeError(err_msg)
        return int(raw_id)

    # --------------------------------------------------
    # INSERT
    # --------------------------------------------------
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()

        # 1) Resolver event_id via event_uuid
        event_uuid = payload.get("event_uuid")
        if not isinstance(event_uuid, str) or not event_uuid:
            raise RuntimeError("event_uuid ausente ou inválido")

        event_resp = (
            sb.table("inventory_events")
            .select("id")
            .eq("uuid", event_uuid)
            .limit(1)
            .execute()
        )

        event_row = self._first_row_as_dict(event_resp, "Evento não encontrado para target")
        event_id = self._row_id_as_int(event_row, "ID inválido do evento")

        # 2) Resolver product_id via product_uuid
        product_uuid = payload.get("product_uuid")
        if not isinstance(product_uuid, str) or not product_uuid:
            raise RuntimeError("product_uuid ausente ou inválido")

        product_resp = (
            sb.table("products")
            .select("id")
            .eq("uuid", product_uuid)
            .limit(1)
            .execute()
        )

        product_row = self._first_row_as_dict(product_resp, "Produto não encontrado para target")
        product_id = self._row_id_as_int(product_row, "ID inválido do produto")

        # 3) Insert do target
        expected_qty = payload.get("expected_qty", 0)

        data = {
            "uuid": record_uuid,
            "company_id": user.company_id,
            "event_id": event_id,
            "product_id": product_id,
            "expected_qty": expected_qty,
            "is_active": True,
        }

        sb.table("inventory_event_targets").insert(data).execute()

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        update_data: Dict[str, Any] = {}

        if "expected_qty" in payload:
            update_data["expected_qty"] = payload["expected_qty"]

        if "is_active" in payload:
            update_data["is_active"] = payload["is_active"]

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update")

        sb = get_supabase_service_client()
        sb.table("inventory_event_targets").update(update_data).eq("uuid", record_uuid).execute()

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser) -> None:
        sb = get_supabase_service_client()
        sb.table("inventory_event_targets").update({"is_active": False}).eq("uuid", record_uuid).execute()
