# backend/app/services/sync/handlers/inventory_items.py

"""
Responsibilities:
- Sync handler for inventory items entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/inventory_items.py

from datetime import datetime, timezone
from typing import cast, Dict, Any, List, Optional

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

        zone_ids_resp = (
            sb.table("zones")
            .select("id, inventory_events!inner(company_id)")
            .eq("inventory_events.company_id", company_id)
            .execute()
        )

        zone_ids: List[int] = []

        for z in zone_ids_resp.data or []:
            if not isinstance(z, dict):
                continue

            raw_id = z.get("id")
            if isinstance(raw_id, (int, str)):
                zone_ids.append(int(raw_id))

        if not zone_ids:
            return []

        query = (
            sb.table("inventory_items")
            .select("*")
            .in_("zone_id", zone_ids)
        )

        if since is not None:
            if isinstance(since, datetime):
                if since.tzinfo is None:
                    since_utc = since.replace(tzinfo=timezone.utc)
                else:
                    since_utc = since.astimezone(timezone.utc)

                query = query.gte("updated_at", since_utc.isoformat())

        result = query.execute()
        return cast(List[Dict[str, Any]], result.data or [])


    # ---------------------------
    # PUSH (INSERT)
    # ---------------------------
    def insert(
        self,
        *,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        sb = get_supabase_service_client()

        zone_id = payload.get("zone_id", payload.get("zone_server_id"))
        if zone_id is None:
            raise RuntimeError("zone_id ausente ou invalido")

        product_id = payload.get("product_id", payload.get("product_server_id"))
        user_id = payload.get("user_id", payload.get("user_server_id", user.db_user_id))
        if user_id is None:
            raise RuntimeError("user_id ausente ou invalido")

        insert_data = {
            "uuid": record_uuid,
            "zone_id": zone_id,
            "product_id": product_id,
            "qty_counted": payload["qty_counted"],
            "device_timestamp": payload["device_timestamp"],
            "source": payload.get("source", "mobile"),
            "user_id": int(user_id),
            "created_by_user_id": int(user_id),
        }

        resp = sb.table("inventory_items").insert(insert_data).execute()

        if not isinstance(resp.data, list) or not resp.data:
            raise RuntimeError("Falha ao inserir inventory_item")

        rows = resp.data

        if not isinstance(rows, list) or len(rows) == 0:
            raise RuntimeError("Falha ao inserir inventory_item")

        row = rows[0]

        if not isinstance(row, dict) or "id" not in row:
            raise RuntimeError("Resposta invalida do Supabase")

        raw_id = row["id"]

        if not isinstance(raw_id, (int, str)):
            raise RuntimeError("ID invalido retornado")

        item_id: int = int(raw_id)

        if not isinstance(item_id, int):
            raise RuntimeError("ID invalido do inventory_item")

        sb.table("inventory_item_events").insert({
            "inventory_item_id": item_id,
            "action": "created",
            "previous_qty": None,
            "new_qty": insert_data["qty_counted"],
            "user_id": int(user_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": "Created via sync",
        }).execute()

    # ---------------------------
    # PUSH (UPDATE)
    # ---------------------------
    def update(
        self,
        *,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        sb = get_supabase_service_client()

        user_id = payload.get("user_id", payload.get("user_server_id", user.db_user_id))
        if user_id is None:
            raise RuntimeError("user_id ausente ou invalido")

        existing = (
            sb.table("inventory_items")
            .select("id, qty_counted")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )

        if not isinstance(existing.data, list) or not existing.data:
            raise RuntimeError("inventory_item nao encontrado")

        row = existing.data[0]
        if not isinstance(row, dict):
            raise RuntimeError("Resposta invalida")

        raw_id = row["id"]

        if not isinstance(raw_id, (int, str)):
            raise RuntimeError("ID invalido")

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
            raise RuntimeError("Nenhum campo valido para update")

        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        sb.table("inventory_items").update(update_data).eq(
            "id", item_id
        ).execute()

        sb.table("inventory_item_events").insert({
            "inventory_item_id": item_id,
            "action": "updated",
            "previous_qty": previous_qty,
            "new_qty": update_data.get("qty_counted", previous_qty),
            "user_id": int(user_id),
            "timestamp": payload.get("device_timestamp")
                or datetime.now(timezone.utc).isoformat(),
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
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("uuid", record_uuid).execute()
