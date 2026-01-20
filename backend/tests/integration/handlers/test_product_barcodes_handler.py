# backend/tests/integration/handlers/test_product_barcodes_handler.py

"""
Responsibilities:
- Test product barcodes handler behavior.
"""

# backend/tests/integration/handlers/test_product_barcodes_handler.py

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
    mod = importlib.import_module("app.services.sync.handlers.product_barcodes")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, BaseSyncHandler):
            if getattr(obj, "table_name", None) == "product_barcodes":
                return obj()
    raise RuntimeError("Handler de product_barcodes não encontrado.")


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
    sb.table("product_barcodes").delete().eq("uuid", uuid).execute()


def test_product_barcodes_pull_bootstrap():
    handler = get_handler()
    data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
    assert isinstance(data, list)
    if data:
        assert data[0]["company_id"] == TEST_COMPANY_ID


def test_product_barcodes_pull_incremental():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    product_id = ensure_product_id()

    sb.table("product_barcodes").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "product_id": product_id,
        "barcode": f"BAR-{record_uuid[:8]}",
        "description": "Barcode incremental",
        "is_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=since)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_product_barcodes_push_insert_and_pull():
    handler = get_handler()
    record_uuid = str(uuid4())
    product_id = ensure_product_id()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)

    payload = {
        "product_id": product_id,
        "barcode": f"BAR-{record_uuid[:8]}",
        "description": "Barcode Push",
        "is_active": True,
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=user)

    try:
        data = handler.pull(company_id=TEST_COMPANY_ID, since=None)
        assert any(r["uuid"] == record_uuid for r in data)
    finally:
        cleanup(record_uuid)


def test_product_barcodes_push_update():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    product_id = ensure_product_id()

    sb.table("product_barcodes").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "product_id": product_id,
        "barcode": f"BAR-{record_uuid[:8]}",
        "description": "Old",
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.update(
        payload={
            "description": "New",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
        record_uuid=record_uuid,
        user=user,
    )

    try:
        resp = sb.table("product_barcodes").select("description").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["description"] == "New"
    finally:
        cleanup(record_uuid)


def test_product_barcodes_push_soft_delete():
    handler = get_handler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())
    product_id = ensure_product_id()

    sb.table("product_barcodes").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "product_id": product_id,
        "barcode": f"BAR-{record_uuid[:8]}",
        "description": "Delete",
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(company_server_id=TEST_COMPANY_ID, db_user_id=TEST_USER_ID)
    handler.delete(payload={}, record_uuid=record_uuid, user=user)

    try:
        resp = sb.table("product_barcodes").select("is_active").eq("uuid", record_uuid).execute()
        assert resp.data and resp.data[0]["is_active"] is False
    finally:
        cleanup(record_uuid)
