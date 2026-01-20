# backend/app/services/sync/handlers/_helpers.py

"""
Responsibilities:
- Sync handler for helpers entities.
- Implement pull and push operations.
"""

#backend/app/services/sync/handlers/_helpers.py

from typing import Any, Optional

from datetime import datetime, timezone


def json_id_to_int(value: Any) -> int:
    """
    Converte valores JSON vindos do Supabase para int de forma segura.
    Lança erro se o valor não for conversível.
    """
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    raise TypeError(f"Valor inválido para ID: {value!r}")

def record_exists_by_uuid(sb, table_name: str, record_uuid: str) -> bool:
    resp = (
        sb.table(table_name)
        .select("id")
        .eq("uuid", record_uuid)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    return bool(data)


def normalize_iso_ts(value: Any) -> str:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str) and value:
        dt = datetime.fromisoformat(value)
    else:
        raise RuntimeError("client_updated_at invalido")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.isoformat()


def should_apply_lww(sb, table_name: str, record_uuid: str, client_updated_at: Any) -> bool:
    client_ts = normalize_iso_ts(client_updated_at)
    resp = (
        sb.table(table_name)
        .select("updated_at")
        .eq("uuid", record_uuid)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    if not data:
        return True
    row = data[0]
    server_ts = row.get("updated_at")
    if not server_ts:
        return True
    server_dt = datetime.fromisoformat(server_ts)
    client_dt = datetime.fromisoformat(client_ts)
    return client_dt > server_dt


def resolve_fk_id(
    sb,
    *,
    table_name: str,
    record_id: Any = None,
    record_uuid: Any = None,
    company_id: Optional[int] = None,
    require_active: bool = False,
    field: str,
) -> int:
    if record_id is None and record_uuid is None:
        raise RuntimeError(f"FK_NOT_RESOLVED:{table_name}:{field}")

    query = sb.table(table_name).select("id, company_id, is_active")
    if record_id is not None:
        query = query.eq("id", record_id)
    else:
        query = query.eq("uuid", record_uuid)

    resp = query.limit(1).execute()
    data = resp.data or []
    if not data:
        raise RuntimeError(f"FK_NOT_RESOLVED:{table_name}:{field}")

    row = data[0]
    if company_id is not None and row.get("company_id") is not None:
        if int(row["company_id"]) != int(company_id):
            raise RuntimeError(f"FK_NOT_RESOLVED:{table_name}:{field}")

    if require_active and "is_active" in row and row.get("is_active") is False:
        raise RuntimeError(f"FK_NOT_RESOLVED:{table_name}:{field}")

    return int(row["id"])


def resolve_zone_id(
    sb,
    *,
    zone_id: Any = None,
    zone_uuid: Any = None,
    company_id: int,
    field: str,
) -> int:
    if zone_id is None and zone_uuid is None:
        raise RuntimeError(f"FK_NOT_RESOLVED:zones:{field}")

    query = (
        sb.table("zones")
        .select("id, is_active, inventory_events!inner(company_id)")
        .eq("inventory_events.company_id", company_id)
    )

    if zone_id is not None:
        query = query.eq("id", zone_id)
    else:
        query = query.eq("uuid", zone_uuid)

    resp = query.limit(1).execute()
    data = resp.data or []
    if not data:
        raise RuntimeError(f"FK_NOT_RESOLVED:zones:{field}")

    row = data[0]
    if row.get("is_active") is False:
        raise RuntimeError(f"FK_NOT_RESOLVED:zones:{field}")

    return int(row["id"])
