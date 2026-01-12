# backend/tests/integration/handlers/test_users_handler.py

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
    mod = importlib.import_module("app.services.sync.handlers.users")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "users":
                return obj()
    raise RuntimeError("Handler de users não encontrado.")


def cleanup(uuid: str):
    sb = get_supabase_service_client()
    sb.table("users").delete().eq("uuid", uuid).execute()


def test_users_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)
    if data:
        assert data[0]["company_id"] == TEST_COMPANY_ID


def test_users_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    sb.table("users").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "email": f"inc-{record_uuid}@test.local",
        "username": f"u_{record_uuid[:8]}",
        "name": "User Incremental",
        "role": "auditor",
        "is_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_users_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())
    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    payload = {
        "email": f"push-{record_uuid}@test.local",
        "username": f"u_{record_uuid[:8]}",
        "name": "User Push Insert",
        "role": "auditor",
        "is_active": True,
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_users_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()
    record_uuid = str(uuid4())

    sb.table("users").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "email": f"old-{record_uuid}@test.local",
        "username": f"u_{record_uuid[:8]}",
        "name": "User Original",
        "role": "auditor",
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.update(payload={"name": "User Atualizado"}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("users").select("name").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["name"] == "User Atualizado"
    finally:
        cleanup(record_uuid)


def test_users_push_soft_delete():
    handler = get_handler()
    sb = get_supabase_service_client()
    record_uuid = str(uuid4())

    sb.table("users").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "email": f"del-{record_uuid}@test.local",
        "username": f"u_{record_uuid[:8]}",
        "name": "User Delete",
        "role": "auditor",
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.delete(payload={}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("users").select("is_active").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["is_active"] is False
    finally:
        cleanup(record_uuid)
