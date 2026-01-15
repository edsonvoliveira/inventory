# backend/tests/integration/handlers/test_inventory_items_handler.py

"""
Responsibilities:
- Test inventory items handler behavior.
"""

# backend/tests/integration/handlers/test_inventory_items_handler.py

import os
import importlib
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.clients.supabase_client import get_supabase_service_client
from app.services.sync.handlers.base import BaseSyncHandler
from tests.helpers.test_user import FakeCurrentUser

TEST_COMPANY_ID = int(os.environ["TEST_COMPANY_ID"])
TEST_USER_ID = 1


def get_handler():
    mod = importlib.import_module("app.services.sync.handlers.inventory_items")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "inventory_items":
                return obj()
    raise RuntimeError("Handler de inventory_items não encontrado.")


def ensure_location_id() -> int:
    sb = get_supabase_service_client()
    resp = sb.table("locations").select("id").eq("company_id", TEST_COMPANY_ID).limit(1).execute()
    if resp.data:
        return int(resp.data[0]["id"])
    loc_uuid = str(uuid4())
    sb.table("locations").insert({
        "uuid": loc_uuid,
        "company_id": TEST_COMPANY_ID,
        "code": f"LOC-{loc_uuid[:6]}",
        "name": "Location Auto (tests)",
        "is_active": True,
    }).execute()
    resp2 = sb.table("locations").select("id").eq("uuid", loc_uuid).limit(1).execute()
    return int(resp2.data[0]["id"])


def ensure_event_id() -> int:
    sb = get_supabase_service_client()
    resp = sb.table("inventory_events").select("id").eq("company_id", TEST_COMPANY_ID).limit(1).execute()
    if resp.data:
        return int(resp.data[0]["id"])
    event_uuid = str(uuid4())
    location_id = ensure_location_id()
    sb.table("inventory_events").insert({
        "uuid": event_uuid,
        "company_id": TEST_COMPANY_ID,
        "location_id": location_id,
        "title": "Evento Auto (tests)",
        "event_type": "full",
        "status": "planned",
        "required_counts": 1,
        "is_active": True,
    }).execute()
    resp2 = sb.table("inventory_events").select("id").eq("uuid", event_uuid).limit(1).execute()
    return int(resp2.data[0]["id"])


def ensure_zone_id() -> int:
    sb = get_supabase_service_client()
    # pega zona cuja event pertence à empresa
    resp = (
        sb.table("zones")
        .select("id, event_id")
        .limit(10)
        .execute()
    )
    if resp.data:
        # tenta achar uma zona cujo event_id pertença à company
        for z in resp.data:
            ev = sb.table("inventory_events").select("company_id").eq("id", z["event_id"]).limit(1).execute()
            if ev.data and int(ev.data[0]["company_id"]) == TEST_COMPANY_ID:
                return int(z["id"])

    # cria
    zone_uuid = str(uuid4())
    event_id = ensure_event_id()
    sb.table("zones").insert({
        "uuid": zone_uuid,
        "event_id": event_id,
        "name": "Zona Auto (tests)",
        "count_status": "not_started",
        "lock_status": "unlocked",
        "is_active": True,
    }).execute()
    resp2 = sb.table("zones").select("id").eq("uuid", zone_uuid).limit(1).execute()
    return int(resp2.data[0]["id"])


def ensure_product_id() -> int:
    sb = get_supabase_service_client()
    resp = sb.table("products").select("id").eq("company_id", TEST_COMPANY_ID).limit(1).execute()
    if resp.data:
        return int(resp.data[0]["id"])

    prod_uuid = str(uuid4())
    sb.table("products").insert({
        "uuid": prod_uuid,
        "company_id": TEST_COMPANY_ID,
        "name": "Produto Auto (tests)",
        "sku": f"SKU-{prod_uuid[:8]}",
        "uom_base": "UN",
        "uom_inventory": "UN",
        "is_active": True,
    }).execute()
    resp2 = sb.table("products").select("id").eq("uuid", prod_uuid).limit(1).execute()
    return int(resp2.data[0]["id"])


def cleanup(uuid: str):
    sb = get_supabase_service_client()
    sb.table("inventory_items").delete().eq("uuid", uuid).execute()


def test_inventory_items_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)


def test_inventory_items_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    zone_id = ensure_zone_id()
    product_id = ensure_product_id()

    sb.table("inventory_items").insert({
        "uuid": record_uuid,
        "zone_id": zone_id,
        "product_id": product_id,
        "qty_counted": 1,
        "device_timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "desktop",
        "user_id": TEST_USER_ID,
        "created_by_user_id": TEST_USER_ID,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_inventory_items_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())

    zone_id = ensure_zone_id()
    product_id = ensure_product_id()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    payload = {
        "zone_id": zone_id,
        "product_id": product_id,
        "qty_counted": 2,
        "device_timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "desktop",
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_inventory_items_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    zone_id = ensure_zone_id()
    product_id = ensure_product_id()

    sb.table("inventory_items").insert({
        "uuid": record_uuid,
        "zone_id": zone_id,
        "product_id": product_id,
        "qty_counted": 1,
        "device_timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "desktop",
        "user_id": TEST_USER_ID,
        "created_by_user_id": TEST_USER_ID,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.update(payload={"qty_counted": 9}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("inventory_items").select("qty_counted").eq("uuid", record_uuid).execute()
        assert resp.data and float(resp.data[0]["qty_counted"]) == 9.0
    finally:
        cleanup(record_uuid)


def test_inventory_items_push_soft_delete():
    """
    Pelo schema do servidor, inventory_items não tem is_active.
    Soft delete deve ser via deleted_at (coluna adicionada no V9).
    Se o seu handler ainda estiver tentando is_active, este teste vai te mostrar isso imediatamente.
    """
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    zone_id = ensure_zone_id()
    product_id = ensure_product_id()

    sb.table("inventory_items").insert({
        "uuid": record_uuid,
        "zone_id": zone_id,
        "product_id": product_id,
        "qty_counted": 1,
        "device_timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "desktop",
        "user_id": TEST_USER_ID,
        "created_by_user_id": TEST_USER_ID,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    handler.delete(payload={}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("inventory_items").select("deleted_at").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["deleted_at"] is not None
    finally:
        cleanup(record_uuid)
