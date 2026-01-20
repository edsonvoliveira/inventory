# backend/tests/integration/handlers/test_products_handler.py

"""
Responsibilities:
- Test products handler behavior.
"""

#backend/tests/integration/handlers/test_products_handler.py

import os
from uuid import uuid4
from datetime import datetime, timedelta, timezone

import pytest

from app.services.sync.handlers.products import ProductSyncHandler
from app.clients.supabase_client import get_supabase_service_client
from tests.helpers.test_user import FakeCurrentUser

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

TEST_COMPANY_ID = int(os.environ["TEST_COMPANY_ID"])
TEST_USER_ID = 1


def cleanup_product(uuid: str):
    sb = get_supabase_service_client()
    sb.table("products").delete().eq("uuid", uuid).execute()


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_products_pull_bootstrap():
    """
    Bootstrap pull:
    - since=None
    - retorna todos os produtos da empresa
    """
    handler = ProductSyncHandler()

    data = handler.pull(
        company_id=TEST_COMPANY_ID,
        since=None,
    )

    assert isinstance(data, list)

    if data:
        row = data[0]
        assert isinstance(row, dict)
        assert "uuid" in row
        assert "company_id" in row
        assert row["company_id"] == TEST_COMPANY_ID


def test_products_pull_incremental():
    """
    Pull incremental:
    - retorna apenas registros atualizados após 'since'
    """
    handler = ProductSyncHandler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())

    sb.table("products").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "name": "Produto Incremental",
        "sku": "SKU-INC",
        "uom_base": "UN",
        "uom_inventory": "UN",
        "is_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    since = datetime.now(timezone.utc) - timedelta(minutes=5)

    data = handler.pull(
        company_id=TEST_COMPANY_ID,
        since=since,
    )

    try:
        assert any(p["uuid"] == record_uuid for p in data)
    finally:
        cleanup_product(record_uuid)


def test_products_push_insert_and_pull():
    """
    Push INSERT:
    - insere no servidor
    - aparece no pull
    """
    handler = ProductSyncHandler()
    record_uuid = str(uuid4())

    user = FakeCurrentUser(
        company_server_id=TEST_COMPANY_ID,
        db_user_id=TEST_USER_ID,
    )

    payload = {
        "name": "Produto Push Insert",
        "sku": "SKU-PUSH",
        "uom_base": "UN",
        "uom_inventory": "UN",
        "is_active": True,
    }

    handler.insert(
        payload=payload,
        record_uuid=record_uuid,
        user=user,
    )

    try:
        data = handler.pull(
            company_id=TEST_COMPANY_ID,
            since=None,
        )

        assert any(p["uuid"] == record_uuid for p in data)
    finally:
        cleanup_product(record_uuid)


def test_products_push_update():
    """
    Push UPDATE:
    - atualiza campos permitidos
    """
    handler = ProductSyncHandler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())

    sb.table("products").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "name": "Produto Original",
        "sku": f"SKU-{record_uuid[:8]}",
        "uom_base": "UN",
        "uom_inventory": "UN",
        "conversion_factor": 1,
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(
        company_server_id=TEST_COMPANY_ID,
        db_user_id=TEST_USER_ID,
    )

    payload = {
        "name": "Produto Atualizado",
        "client_updated_at": datetime.now(timezone.utc).isoformat(),
    }

    handler.update(
        payload=payload,
        record_uuid=record_uuid,
        user=user,
    )

    try:
        resp = (
            sb.table("products")
            .select("name")
            .eq("uuid", record_uuid)
            .execute()
        )

        assert isinstance(resp.data, list)
        assert len(resp.data) == 1

        updated = resp.data[0]
        assert isinstance(updated, dict)
        assert updated["name"] == "Produto Atualizado"
    finally:
        cleanup_product(record_uuid)


def test_products_push_soft_delete():
    """
    Push DELETE:
    - soft delete (is_active = false)
    """
    handler = ProductSyncHandler()
    sb = get_supabase_service_client()

    record_uuid = str(uuid4())

    sb.table("products").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "name": "Produto Delete",
        "sku": f"SKU-{record_uuid[:8]}",
        "uom_base": "UN",
        "uom_inventory": "UN",
        "conversion_factor": 1,
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(
        company_server_id=TEST_COMPANY_ID,
        db_user_id=TEST_USER_ID,
    )

    handler.delete(
        payload={},
        record_uuid=record_uuid,
        user=user,
    )

    try:
        resp = (
            sb.table("products")
            .select("is_active")
            .eq("uuid", record_uuid)
            .execute()
        )

        assert isinstance(resp.data, list)
        assert len(resp.data) == 1

        row = resp.data[0]
        assert isinstance(row, dict)
        assert row["is_active"] is False
    finally:
        cleanup_product(record_uuid)
