# backend/app/services/sync_service.py

from datetime import datetime, timezone
from typing import List, Dict, Any

from app.clients.supabase_client import get_supabase_service_client
from app.schemas.sync import SyncItem
from app.core.security import CurrentUser

from app.services.sync.registry import SYNC_HANDLERS

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
    accepted, failed = [], []

    for item in items:
        handler = SYNC_HANDLERS.get(item.table_name)

        if not handler:
            failed.append(item.record_uuid)
            continue

        try:
            if item.operation == "insert":
                handler.insert(item.payload, item.record_uuid, user)
            elif item.operation == "update":
                handler.update(item.payload, item.record_uuid, user)
            elif item.operation == "delete":
                handler.delete(item.payload, item.record_uuid, user)
            else:
                raise RuntimeError("Operação inválida")

            accepted.append(item.record_uuid)

        except Exception as e:
            print(f"❌ ERRO SYNC {item.table_name.upper()}:", e)
            failed.append(item.record_uuid)

    return accepted, failed