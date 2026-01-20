# backend/tests/integration/handlers/test_product_categories_handler.py

"""
Responsibilities:
- Test product categories handler behavior.
"""

#backend/tests/integration/handlers/test_product_categories_handler.py

import os
import importlib
from uuid import uuid4
from datetime import datetime, timezone
from datetime import datetime, timedelta, timezone

from app.clients.supabase_client import get_supabase_service_client
from app.services.sync.handlers.base import BaseSyncHandler
from tests.helpers.test_user import FakeCurrentUser

TEST_COMPANY_ID = int(os.environ["TEST_COMPANY_ID"])
TEST_USER_ID = 1


def get_handler():
    mod = importlib.import_module("app.services.sync.handlers.product_categories")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "product_categories":
                return obj()
    raise RuntimeError("Handler de product_categories não encontrado (table_name mismatch).")


def cleanup(uuid: str):
    sb = get_supabase_service_client()
    sb.table("product_categories").delete().eq("uuid", uuid).execute()


def test_product_categories_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)
    if data:
        row = data[0]
        assert isinstance(row, dict)
        assert row["company_id"] == TEST_COMPANY_ID


def test_product_categories_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    sb.table("product_categories").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "code": "CAT-INC",
        "name": "Categoria Incremental",
        "is_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_product_categories_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    payload = {
        "code": "CAT-PUSH",
        "name": "Categoria Push Insert",
        "description": "desc",
        "is_active": True,
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_product_categories_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    sb.table("product_categories").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "code": f"CAT-{record_uuid[:8]}",
        "name": "Categoria Original",
        "description": None,
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    handler.update(
        payload={
            "name": "Categoria Atualizada",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
        record_uuid=record_uuid,
        user=user,
    )

    try:
        resp = sb.table("product_categories").select("name").eq("uuid", record_uuid).execute()
        assert isinstance(resp.data, list) and len(resp.data) == 1
        row = resp.data[0]
        assert isinstance(row, dict)
        assert row["name"] == "Categoria Atualizada"
    finally:
        cleanup(record_uuid)


def test_product_categories_push_soft_delete():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    sb.table("product_categories").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "code": f"CAT-{record_uuid[:8]}",
        "name": "Categoria Delete",
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.delete(payload={}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("product_categories").select("is_active").eq("uuid", record_uuid).execute()
        assert isinstance(resp.data, list) and len(resp.data) == 1
        row = resp.data[0]
        assert isinstance(row, dict)
        assert row["is_active"] is False
    finally:
        cleanup(record_uuid)
