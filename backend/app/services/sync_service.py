# app/services/sync_service.py

from datetime import datetime, timezone
from typing import List, Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.schemas.sync import SyncItem
from app.core.security import CurrentUser


# ======================================================
# BOOTSTRAP SYNC (FULL INITIAL LOAD)
# ======================================================

async def bootstrap_sync(user: CurrentUser) -> Dict[str, Any]:
    """
    Retorna todos os dados iniciais necessários
    para inicialização do Desktop/Mobile.
    """

    sb = get_supabase_service_client()

    # Resolve company_id a partir do supabase_auth_id
    ctx_resp = (
        sb.table("users")
        .select("company_id")
        .eq("supabase_auth_id", user.auth_uid)
        .limit(1)
        .execute()
    )

    data = ctx_resp.data

    # Normalização explícita de tipo (importante para Pylance)
    if not isinstance(data, list) or len(data) == 0:
        raise RuntimeError("Usuário não associado a nenhuma empresa")

    row = data[0]

    if not isinstance(row, dict) or "company_id" not in row:
        raise RuntimeError("company_id inválido retornado pelo Supabase")

    raw_company_id = row["company_id"]

    if not isinstance(raw_company_id, (int, str)):
        raise RuntimeError("company_id inválido retornado pelo Supabase")

    company_id: int = int(raw_company_id)

    def fetch(table: str, **filters):
        q = sb.table(table).select("*")
        for k, v in filters.items():
            q = q.eq(k, v)
        return q.execute().data or []

    return {
        "company": fetch("companies", id=company_id)[0],
        "users": fetch("users", company_id=company_id),
        "locations": fetch("locations", company_id=company_id),
        "product_categories": fetch("product_categories", company_id=company_id),
        "products": fetch("products", company_id=company_id),
        "product_barcodes": fetch("product_barcodes", company_id=company_id),
        "inventory_events": fetch("inventory_events", company_id=company_id),
        "inventory_event_targets": fetch("inventory_event_targets", company_id=company_id),
        "zones": fetch("zones"),
        "server_ts": datetime.now(timezone.utc).isoformat(),
    }


# ======================================================
# SYNC PUSH (OUTBOX)
# ======================================================

def process_sync_items(items: list[SyncItem], user: CurrentUser):
    accepted: list[str] = []
    failed: list[str] = []

    sb = get_supabase_service_client()

    # ======================================================
    # 1️⃣ Resolver user_id interno a partir do JWT
    # ======================================================
    user_resp = (
        sb.table("users")
        .select("id")
        .eq("supabase_auth_id", user.auth_uid)
        .limit(1)
        .execute()
    )

    if not user_resp.data or not isinstance(user_resp.data, list):
        raise RuntimeError("Usuário autenticado não encontrado na tabela users")

    data = user_resp.data

    if not isinstance(data, list) or len(data) == 0:
        raise RuntimeError("Usuário autenticado não encontrado na tabela users")

    row = data[0]

    if not isinstance(row, dict) or "id" not in row:
        raise RuntimeError("Resposta inválida ao resolver user_id")

    raw_id = row["id"]

    if not isinstance(raw_id, (int, str)):
        raise RuntimeError("ID inválido retornado pelo Supabase")

    resolved_user_id: int = int(raw_id)

    # ======================================================
    # 2️⃣ Processar itens da outbox
    # ======================================================
    for item in items:
        try:
            if item.table_name == "inventory_items" and item.operation == "insert":
                payload = item.payload

                insert_data = {
                    "uuid": item.record_uuid,
                    "zone_id": payload["zone_id"],              # server_id
                    "product_id": payload.get("product_id"),   # server_id ou None
                    "qty_counted": payload["qty_counted"],
                    "device_timestamp": payload["device_timestamp"],
                    "source": payload.get("source", "mobile"),

                    # 🔒 Segurança: user vem SEMPRE do JWT
                    "user_id": resolved_user_id,
                    "created_by_user_id": resolved_user_id,
                }

                sb.table("inventory_items").insert(insert_data).execute()

                # 1) Inserir inventory_item
                insert_resp = (
                    sb.table("inventory_items")
                    .insert(insert_data)
                    .execute()
                )

                # Garantir retorno válido
                rows = insert_resp.data
                if not isinstance(rows, list) or len(rows) == 0 or not isinstance(rows[0], dict):
                    raise RuntimeError("Falha ao inserir inventory_item")

                inventory_item_id = rows[0].get("id")
                if not isinstance(inventory_item_id, int):
                    raise RuntimeError("ID do inventory_item inválido")

                # 2) Criar evento de auditoria (inventory_item_events)
                event_data = {
                    "inventory_item_id": inventory_item_id,
                    "action": "created",
                    "previous_qty": None,
                    "new_qty": insert_data["qty_counted"],
                    "user_id": insert_data["user_id"],
                    "device_id": payload.get("device_id"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "notes": "Created via sync_push",
                }

                sb.table("inventory_item_events").insert(event_data).execute()


                accepted.append(item.record_uuid)
                continue

            # fallback (tabelas/ações ainda não implementadas)
            failed.append(item.record_uuid)

        except Exception as e:
            print("❌ ERRO SYNC INVENTORY_ITEM:", e)
            failed.append(item.record_uuid)

    return accepted, failed

