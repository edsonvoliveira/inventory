# backend/app/services/sync/inventory_items.py

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.services.sync.handlers.base import BaseSyncHandler
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext


class InventoryItemSyncHandler(BaseSyncHandler):
    table_name = "inventory_items"

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
            .select(
                "*, inventory_events!inner(company_id)"
            )
            .eq("inventory_events.company_id", company_id)
            .eq("is_active", True)
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

        insert_data = {
            "uuid": record_uuid,
            "zone_id": payload["zone_id"],
            "product_id": payload.get("product_id"),
            "qty_counted": payload["qty_counted"],
            "device_timestamp": payload["device_timestamp"],
            "source": payload.get("source", "mobile"),
            "user_id": user.db_user_id,
            "created_by_user_id": user.db_user_id,
        }

        resp = sb.table("inventory_items").insert(insert_data).execute()

        if not isinstance(resp.data, list) or not resp.data:
            raise RuntimeError("Falha ao inserir inventory_item")

        rows = resp.data

        if not isinstance(rows, list) or len(rows) == 0:
            raise RuntimeError("Falha ao inserir inventory_item")

        row = rows[0]

        if not isinstance(row, dict) or "id" not in row:
            raise RuntimeError("Resposta inválida do Supabase")

        raw_id = row["id"]

        if not isinstance(raw_id, (int, str)):
            raise RuntimeError("ID inválido retornado")

        item_id: int = int(raw_id)

        if not isinstance(item_id, int):
            raise RuntimeError("ID inválido do inventory_item")

        sb.table("inventory_item_events").insert({
            "inventory_item_id": item_id,
            "action": "created",
            "previous_qty": None,
            "new_qty": insert_data["qty_counted"],
            "user_id": user.db_user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": "Created via sync",
        }).execute()

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

        existing = (
            sb.table("inventory_items")
            .select("id, qty_counted")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )

        if not isinstance(existing.data, list) or not existing.data:
            raise RuntimeError("inventory_item não encontrado")

        row = existing.data[0]
        if not isinstance(row, dict):
            raise RuntimeError("Resposta inválida")

        raw_id = row["id"]

        if not isinstance(raw_id, (int, str)):
            raise RuntimeError("ID inválido")

        item_id = int(raw_id)

        previous_qty = row.get("qty_counted")

        allowed_fields = [
            "qty_counted",
            "batch_number",
            "expiry_date",
            "scanned_code",
            "device_timestamp",
            "latitude",
            "longitude",
            "source",
        ]

        update_data = {
            k: payload[k]
            for k in allowed_fields
            if k in payload
        }

        if not update_data:
            raise RuntimeError("Nenhum campo válido para update")

        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        sb.table("inventory_items").update(update_data).eq(
            "id", item_id
        ).execute()

        sb.table("inventory_item_events").insert({
            "inventory_item_id": item_id,
            "action": "updated",
            "previous_qty": previous_qty,
            "new_qty": update_data.get("qty_counted", previous_qty),
            "user_id": user.db_user_id,
            "timestamp": update_data.get("device_timestamp"),
            "notes": "Updated via sync",
        }).execute()

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

        sb.table("inventory_items").update({
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("uuid", record_uuid).execute()
