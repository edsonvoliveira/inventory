# backend/tests/integration/handlers/test_zone_user_progress_handler.py

"""
Responsibilities:
- Test zone user progress handler behavior.
"""

# backend/tests/integration/handlers/test_zone_user_progress_handler.py

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
    mod = importlib.import_module("app.services.sync.handlers.zone_user_progress")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "zone_user_progress":
                return obj()
    raise RuntimeError("Handler de zone_user_progress não encontrado.")


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
    # tenta achar zona pertencente à company
    resp = sb.table("zones").select("id, event_id").limit(10).execute()
    if resp.data:
        for z in resp.data:
            ev = sb.table("inventory_events").select("company_id").eq("id", z["event_id"]).limit(1).execute()
            if ev.data and int(ev.data[0]["company_id"]) == TEST_COMPANY_ID:
                return int(z["id"])

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


def cleanup(uuid: str):
    sb = get_supabase_service_client()
    sb.table("zone_user_progress").delete().eq("uuid", uuid).execute()


def test_zone_user_progress_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)


def test_zone_user_progress_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    zone_id = ensure_zone_id()

    sb.table("zone_user_progress").insert({
        "uuid": record_uuid,
        "zone_id": zone_id,
        "user_id": TEST_USER_ID,
        "count_type": "primary",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "is_finished": False,
        "items_counted": 0,
        "qty_total": 0,
        "device_id": "desktop",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_zone_user_progress_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())
    zone_id = ensure_zone_id()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    payload = {
        "zone_id": zone_id,
        "user_id": TEST_USER_ID,
        "count_type": "primary",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "is_finished": False,
        "items_counted": 0,
        "qty_total": 0,
        "device_id": "desktop",
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_zone_user_progress_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()
    record_uuid = str(uuid4())
    zone_id = ensure_zone_id()

    sb.table("zone_user_progress").insert({
        "uuid": record_uuid,
        "zone_id": zone_id,
        "user_id": TEST_USER_ID,
        "count_type": "primary",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "is_finished": False,
        "items_counted": 0,
        "qty_total": 0,
        "device_id": "desktop",
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.update(payload={"items_counted": 10, "qty_total": 100}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("zone_user_progress").select("items_counted, qty_total").eq("uuid", record_uuid).execute()
        assert resp.data and int(resp.data[0]["items_counted"]) == 10
    finally:
        cleanup(record_uuid)
