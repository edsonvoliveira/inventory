# backend/tests/integration/handlers/test_inventory_event_targets_handler.py

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
    mod = importlib.import_module("app.services.sync.handlers.inventory_event_targets")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "inventory_event_targets":
                return obj()
    raise RuntimeError("Handler de inventory_event_targets não encontrado.")

def cleanup_target(event_id: int, product_id: int):
    sb = get_supabase_service_client()
    sb.table("inventory_event_targets") \
        .delete() \
        .eq("event_id", event_id) \
        .eq("product_id", product_id) \
        .execute()

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
    sb.table("inventory_event_targets").delete().eq("uuid", uuid).execute()

def test_inventory_event_targets_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)
    if data:
        assert data[0]["company_id"] == TEST_COMPANY_ID


def test_inventory_event_targets_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    event_id = ensure_event_id()
    product_id = ensure_product_id()

    cleanup_target(event_id, product_id)

    sb.table("inventory_event_targets").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "event_id": event_id,
        "product_id": product_id,
        "expected_qty": 10,
        "is_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_inventory_event_targets_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())
    event_id = ensure_event_id()
    product_id = ensure_product_id()

    sb = get_supabase_service_client()

    event_resp = (
        sb.table("inventory_events")
        .select("uuid")
        .eq("id", event_id)
        .single()
        .execute()
    )

    assert event_resp.data is not None
    assert isinstance(event_resp.data, dict)

    event_uuid = event_resp.data["uuid"]

    product_resp = (
        sb.table("products")
        .select("uuid")
        .eq("id", product_id)
        .single()
        .execute()
    )

    assert product_resp.data is not None
    assert isinstance(product_resp.data, dict)

    product_uuid = product_resp.data["uuid"]

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    payload = {
        "event_uuid": event_uuid,
        "product_uuid": product_uuid,
        "expected_qty": 5,
        "is_active": True,
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_inventory_event_targets_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    event_id = ensure_event_id()
    product_id = ensure_product_id()

    sb.table("inventory_event_targets").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "event_id": event_id,
        "product_id": product_id,
        "expected_qty": 1,
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.update(payload={"expected_qty": 99}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("inventory_event_targets").select("expected_qty").eq("uuid", record_uuid).execute()
        assert resp.data and float(resp.data[0]["expected_qty"]) == 99.0
    finally:
        cleanup(record_uuid)


def test_inventory_event_targets_push_soft_delete():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    event_id = ensure_event_id()
    product_id = ensure_product_id()

    sb.table("inventory_event_targets").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "event_id": event_id,
        "product_id": product_id,
        "expected_qty": 1,
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.delete(payload={}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("inventory_event_targets").select("is_active").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["is_active"] is False
    finally:
        cleanup(record_uuid)
