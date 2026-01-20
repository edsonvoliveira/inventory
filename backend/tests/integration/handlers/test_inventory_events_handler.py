# backend/tests/integration/handlers/test_inventory_events_handler.py

"""
Responsibilities:
- Test inventory events handler behavior.
"""

# backend/tests/integration/handlers/test_inventory_events_handler.py

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
    mod = importlib.import_module("app.services.sync.handlers.inventory_events")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "inventory_events":
                return obj()
    raise RuntimeError("Handler de inventory_events não encontrado.")


def ensure_location_id() -> int:
    sb = get_supabase_service_client()
    resp = sb.table("locations").select("id").eq("company_id", TEST_COMPANY_ID).limit(1).execute()
    if resp.data:
        return int(resp.data[0]["id"])

    # cria uma location se não existir
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


def cleanup(uuid: str):
    sb = get_supabase_service_client()
    sb.table("inventory_events").delete().eq("uuid", uuid).execute()


def test_inventory_events_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)
    if data:
        assert data[0]["company_id"] == TEST_COMPANY_ID


def test_inventory_events_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    location_id = ensure_location_id()

    sb.table("inventory_events").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "location_id": location_id,
        "title": "Evento Incremental",
        "event_type": "full",
        "status": "planned",
        "required_counts": 1,
        "is_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_inventory_events_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())
    location_id = ensure_location_id()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    payload = {
        "location_id": location_id,
        "title": "Evento Push Insert",
        "event_type": "full",
        "status": "planned",
        "required_counts": 1,
        "is_active": True,
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_inventory_events_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    location_id = ensure_location_id()

    sb.table("inventory_events").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "location_id": location_id,
        "title": "Evento Original",
        "event_type": "full",
        "status": "planned",
        "required_counts": 1,
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.update(
        payload={
            "title": "Evento Atualizado",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
        record_uuid=record_uuid,
        user=user,
    )

    try:
        resp = sb.table("inventory_events").select("title").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["title"] == "Evento Atualizado"
    finally:
        cleanup(record_uuid)


def test_inventory_events_push_soft_delete():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    location_id = ensure_location_id()

    sb.table("inventory_events").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "location_id": location_id,
        "title": "Evento Delete",
        "event_type": "full",
        "status": "planned",
        "required_counts": 1,
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.delete(payload={}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("inventory_events").select("is_active").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["is_active"] is False
    finally:
        cleanup(record_uuid)
