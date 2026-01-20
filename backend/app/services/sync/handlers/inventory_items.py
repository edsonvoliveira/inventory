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
from app.services.sync.handlers._helpers import record_exists_by_uuid, should_apply_lww, resolve_fk_id, resolve_zone_id
from app.clients.supabase_client import get_supabase_service_client
from app.core.user_context import UserContext
from app.services.sync.handlers._time import normalize_ts


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
        if record_exists_by_uuid(sb, self.table_name, record_uuid):
            return

        zone_id = resolve_zone_id(
            sb,
            zone_id=payload.get("zone_id", payload.get("zone_server_id")),
            zone_uuid=payload.get("zone_uuid"),
            company_id=user.company_server_id,
            field="zone_id",
        )

        product_id = payload.get("product_id", payload.get("product_server_id"))
        if product_id or payload.get("product_uuid"):
            product_id = resolve_fk_id(
                sb,
                table_name="products",
                record_id=product_id,
                record_uuid=payload.get("product_uuid"),
                company_id=user.company_server_id,
                require_active=True,
                field="product_id",
            )

        user_id = resolve_fk_id(
            sb,
            table_name="users",
            record_id=payload.get("user_id", payload.get("user_server_id", user.db_user_id)),
            record_uuid=payload.get("user_uuid"),
            company_id=user.company_server_id,
            require_active=True,
            field="user_id",
        )

        insert_data = {
            "uuid": record_uuid,
            "zone_id": zone_id,
            "product_id": product_id,
            "qty_counted": payload["qty_counted"],
            "device_timestamp": normalize_ts(payload.get("device_timestamp"), field="device_timestamp"),
            "source": payload.get("source", "mobile"),
            "user_id": int(user_id),
            "created_by_user_id": int(user_id),
        }

        resp = sb.table("inventory_items").insert(insert_data).execute()

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
        if not should_apply_lww(sb, self.table_name, record_uuid, payload.get("client_updated_at")):
            return

        user_id = resolve_fk_id(
            sb,
            table_name="users",
            record_id=payload.get("user_id", payload.get("user_server_id", user.db_user_id)),
            record_uuid=payload.get("user_uuid"),
            company_id=user.company_server_id,
            require_active=True,
            field="user_id",
        )

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

        self._reject_unknown_fields(payload, allowed_fields=allowed_fields + ["user_id", "user_server_id", "client_updated_at"])

        update_data = {
            k: payload[k]
            for k in allowed_fields
            if k in payload
        }

        if not update_data:
            raise RuntimeError("Nenhum campo valido para update")

        if "device_timestamp" in update_data:
            update_data["device_timestamp"] = normalize_ts(
                update_data["device_timestamp"],
                field="device_timestamp",
            )

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
            "timestamp": update_data.get("device_timestamp")
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
        raise RuntimeError("inventory_items nao suportam delete via sync")



