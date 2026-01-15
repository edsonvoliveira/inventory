# backend/tests/integration/handlers/test_devices_handler.py

"""
Responsibilities:
- Test devices handler behavior.
"""

# backend/tests/integration/handlers/test_devices_handler.py

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
    mod = importlib.import_module("app.services.sync.handlers.devices")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "devices":
                return obj()
    raise RuntimeError("Handler de devices não encontrado.")


def cleanup(uuid: str):
    sb = get_supabase_service_client()
    sb.table("devices").delete().eq("uuid", uuid).execute()


def test_devices_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)


def test_devices_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())

    sb.table("devices").insert({
        "uuid": record_uuid,
        "device_uuid": f"DEV-{record_uuid[:8]}",
        "user_id": TEST_USER_ID,
        "os": "windows",
        "app_version": "1.0",
        "is_blocked": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_devices_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    payload = {
        "device_uuid": f"DEV-{record_uuid[:8]}",
        "os": "windows",
        "app_version": "1.0",
        "last_sync_at": datetime.now(timezone.utc).isoformat(),
        "is_blocked": False,
        "metadata": {"k": "v"},
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_devices_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()
    record_uuid = str(uuid4())

    sb.table("devices").insert({
        "uuid": record_uuid,
        "device_uuid": f"DEV-{record_uuid[:8]}",
        "user_id": TEST_USER_ID,
        "os": "windows",
        "app_version": "1.0",
        "is_blocked": False,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.update(payload={"app_version": "2.0"}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("devices").select("app_version").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["app_version"] == "2.0"
    finally:
        cleanup(record_uuid)


def test_devices_push_soft_delete_blocks_device():
    handler = get_handler()
    sb = get_supabase_service_client()
    record_uuid = str(uuid4())

    sb.table("devices").insert({
        "uuid": record_uuid,
        "device_uuid": f"DEV-{record_uuid[:8]}",
        "user_id": TEST_USER_ID,
        "os": "windows",
        "app_version": "1.0",
        "is_blocked": False,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.delete(payload={}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("devices").select("is_blocked").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["is_blocked"] is True
    finally:
        cleanup(record_uuid)
