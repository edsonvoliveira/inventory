# backend/tests/helpers/sync_data.py

"""
Responsibilities:
- Helpers to create and cleanup test data for sync integration tests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def _fetch_row_by_uuid(sb, table: str, record_uuid: str) -> dict:
    resp = (
        sb.table(table)
        .select("id, uuid")
        .eq("uuid", record_uuid)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    if not data:
        raise RuntimeError(f"Registro nao encontrado: {table}:{record_uuid}")
    row = data[0]
    if not isinstance(row, dict):
        raise RuntimeError(f"Resposta invalida: {table}:{record_uuid}")
    return row


def cleanup_by_uuid(sb, table: str, record_uuid: str) -> None:
    sb.table(table).delete().eq("uuid", record_uuid).execute()


def create_location(sb, company_id: int, name: str | None = None) -> dict:
    record_uuid = str(uuid4())
    code = f"LOC-{record_uuid[:8]}"
    payload = {
        "uuid": record_uuid,
        "company_id": company_id,
        "code": code,
        "name": name or f"Location {record_uuid[:8]}",
        "is_active": True,
    }
    sb.table("locations").insert(payload).execute()
    return _fetch_row_by_uuid(sb, "locations", record_uuid)


def create_product_category(sb, company_id: int, name: str | None = None) -> dict:
    record_uuid = str(uuid4())
    code = f"CAT-{record_uuid[:8]}"
    payload = {
        "uuid": record_uuid,
        "company_id": company_id,
        "code": code,
        "name": name or f"Category {record_uuid[:8]}",
        "is_active": True,
    }
    sb.table("product_categories").insert(payload).execute()
    return _fetch_row_by_uuid(sb, "product_categories", record_uuid)


def create_product(
    sb,
    company_id: int,
    *,
    category_id: int | None = None,
    name: str | None = None,
) -> dict:
    record_uuid = str(uuid4())
    payload = {
        "uuid": record_uuid,
        "company_id": company_id,
        "category_id": category_id,
        "sku": f"SKU-{record_uuid[:8]}",
        "name": name or f"Product {record_uuid[:8]}",
        "uom_base": "UN",
        "uom_inventory": "UN",
        "conversion_factor": 1,
        "is_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    sb.table("products").insert(payload).execute()
    return _fetch_row_by_uuid(sb, "products", record_uuid)


def create_user(
    sb,
    company_id: int,
    *,
    name: str | None = None,
    email: str | None = None,
    role: str = "auditor",
    is_active: bool = True,
) -> dict:
    record_uuid = str(uuid4())
    payload = {
        "uuid": record_uuid,
        "company_id": company_id,
        "email": email or f"user-{record_uuid[:8]}@test.local",
        "name": name or f"User {record_uuid[:8]}",
        "role": role,
        "is_active": is_active,
    }
    sb.table("users").insert(payload).execute()
    return _fetch_row_by_uuid(sb, "users", record_uuid)


def create_event(
    sb,
    company_id: int,
    *,
    location_id: int,
    status: str = "open",
    required_counts: int = 1,
) -> dict:
    record_uuid = str(uuid4())
    payload = {
        "uuid": record_uuid,
        "company_id": company_id,
        "location_id": location_id,
        "title": f"Event {record_uuid[:8]}",
        "event_type": "count",
        "status": status,
        "required_counts": required_counts,
        "is_active": True,
    }
    sb.table("inventory_events").insert(payload).execute()
    return _fetch_row_by_uuid(sb, "inventory_events", record_uuid)


def create_zone(sb, *, event_id: int, name: str | None = None) -> dict:
    record_uuid = str(uuid4())
    payload = {
        "uuid": record_uuid,
        "event_id": event_id,
        "name": name or f"Zone {record_uuid[:8]}",
        "count_status": "not_started",
        "lock_status": "unlocked",
        "is_active": True,
    }
    sb.table("zones").insert(payload).execute()
    return _fetch_row_by_uuid(sb, "zones", record_uuid)


def create_device(
    sb,
    *,
    user_id: int | None,
    device_uuid: str | None = None,
    is_blocked: bool = False,
) -> dict:
    record_uuid = str(uuid4())
    payload = {
        "uuid": record_uuid,
        "device_uuid": device_uuid or f"device-{record_uuid[:8]}",
        "user_id": user_id,
        "os": "test",
        "app_version": "0.1.0",
        "is_blocked": is_blocked,
    }
    sb.table("devices").insert(payload).execute()
    return _fetch_row_by_uuid(sb, "devices", record_uuid)
