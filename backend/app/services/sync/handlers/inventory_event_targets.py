# backend/app/services/sync/handlers/inventory_event_targets.py

"""
Responsibilities:
- Sync handler for inventory event targets entities.
- Implement pull and push operations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class InventoryEventTargetSyncHandler(BaseSyncHandler):
    table_name = "inventory_event_targets"

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

    # --------------------------------------------------
    # Helpers (normalizacao para Pylance + robustez)
    # --------------------------------------------------
    def _first_row_as_dict(self, resp, err_msg: str) -> Dict[str, Any]:
        """
        Converte resp.data (List[JSON] | None) em Dict[str, Any] com validacoes.
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

    # ---------------------------
    # PUSH (INSERT)
    # ---------------------------
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()

        event_id = payload.get("event_id", payload.get("event_server_id"))
        if event_id is None:
            event_uuid = payload.get("event_uuid")
            if not isinstance(event_uuid, str) or not event_uuid:
                raise RuntimeError("event_uuid ausente ou invalido")

            event_resp = (
                sb.table("inventory_events")
                .select("id")
                .eq("uuid", event_uuid)
                .limit(1)
                .execute()
            )

            event_row = self._first_row_as_dict(event_resp, "Evento nao encontrado para target")
            event_id = self._row_id_as_int(event_row, "ID invalido do evento")

        product_id = payload.get("product_id", payload.get("product_server_id"))
        if product_id is None:
            product_uuid = payload.get("product_uuid")
            if not isinstance(product_uuid, str) or not product_uuid:
                raise RuntimeError("product_uuid ausente ou invalido")

            product_resp = (
                sb.table("products")
                .select("id")
                .eq("uuid", product_uuid)
                .limit(1)
                .execute()
            )

            product_row = self._first_row_as_dict(product_resp, "Produto nao encontrado para target")
            product_id = self._row_id_as_int(product_row, "ID invalido do produto")

        expected_qty = payload.get("expected_qty", 0)

        data = {
            "uuid": record_uuid,
            "company_id": user.company_server_id,
            "event_id": int(event_id),
            "product_id": int(product_id),
            "expected_qty": expected_qty,
            "is_active": True,
        }

        sb.table("inventory_event_targets").insert(data).execute()

    def update(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        update_data: Dict[str, Any] = {}

        if "expected_qty" in payload:
            update_data["expected_qty"] = payload["expected_qty"]

        if "is_active" in payload:
            update_data["is_active"] = payload["is_active"]

        if not update_data:
            raise RuntimeError("Nenhum campo valido para update")

        sb = get_supabase_service_client()
        sb.table("inventory_event_targets").update(update_data).eq("uuid", record_uuid).execute()

    # ---------------------------
    # PUSH (DELETE)
    # ---------------------------
    def delete(self, payload: Dict[str, Any], record_uuid: str, user: UserContext) -> None:
        sb = get_supabase_service_client()
        sb.table("inventory_event_targets").update({"is_active": False}).eq("uuid", record_uuid).execute()
