# backend/app/services/sync_service.py
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

from app.clients.supabase_client import get_supabase_service_client

def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not isinstance(data, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            out.append(item)
    return out

def _with_server_id(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Adiciona server_id = id (compatibilidade com SQLite repos)
    out: List[Dict[str, Any]] = []
    for r in rows:
        rr = dict(r)
        if "id" in rr and "server_id" not in rr:
            rr["server_id"] = rr["id"]
        out.append(rr)
    return out

async def bootstrap_sync(user):
    sb = get_supabase_service_client()

    # 1) Resolver company_id a partir do user autenticado (via tabela public.users)
    # A sua tabela usa: supabase_auth_id
    # (Não use auth_uid no SQL; o campo chama supabase_auth_id)
    me = sb.table("users").select("company_id").eq("supabase_auth_id", user.auth_uid).limit(1).execute()
    me_rows = _as_list_of_dicts(me.data)
    if not me_rows or "company_id" not in me_rows[0]:
        raise RuntimeError("Contexto do usuário não encontrado (company_id)")

    company_id = int(me_rows[0]["company_id"])

    # 2) Fetch helper
    def fetch(table: str, **filters: Any) -> List[Dict[str, Any]]:
        q = sb.table(table).select("*")
        for k, v in filters.items():
            q = q.eq(k, v)
        resp = q.execute()
        rows = _as_list_of_dicts(resp.data)
        return _with_server_id(rows)

    company_rows = fetch("companies", id=company_id)
    if not company_rows:
        raise RuntimeError("Empresa não encontrada no servidor")

    # 3) Payload bootstrap (tudo com server_id)
    return {
        "company": company_rows[0],
        "users": fetch("users", company_id=company_id),
        "locations": fetch("locations", company_id=company_id),
        "product_categories": fetch("product_categories", company_id=company_id),
        "products": fetch("products", company_id=company_id),
        "product_barcodes": fetch("product_barcodes", company_id=company_id),
        "inventory_events": fetch("inventory_events", company_id=company_id),
        "inventory_event_targets": fetch("inventory_event_targets", company_id=company_id),
        # zonas dependem de eventos; por simplicidade agora trazemos todas e filtramos no desktop depois
        "zones": fetch("zones"),
        "server_ts": datetime.now(timezone.utc).isoformat(),
    }
