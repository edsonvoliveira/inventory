#backend/tests/integration/handlers/test_products_handler.py

import os
from uuid import uuid4
from datetime import datetime, timedelta, timezone

import pytest

from app.services.sync.handlers.products import ProductSyncHandler
from app.clients.supabase_client import get_supabase_service_client


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

class FakeCurrentUser:
    def __init__(self, company_server_id: int, db_user_id: int):
        self.company_server_id = company_server_id
        self.db_user_id = db_user_id


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

    record_uuid = f"test-inc-{uuid4()}"

    sb.table("products").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "name": "Produto Incremental",
        "sku": "SKU-INC",
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
    record_uuid = f"test-insert-{uuid4()}"

    user = FakeCurrentUser(
        company_server_id=TEST_COMPANY_ID,
        db_user_id=TEST_USER_ID,
    )

    payload = {
        "name": "Produto Push Insert",
        "sku": "SKU-PUSH",
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

    record_uuid = f"test-update-{uuid4()}"

    sb.table("products").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "name": "Produto Original",
        "sku": "SKU-OLD",
        "is_active": True,
    }).execute()

    user = FakeCurrentUser(
        company_server_id=TEST_COMPANY_ID,
        db_user_id=TEST_USER_ID,
    )

    payload = {
        "name": "Produto Atualizado",
    }

    handler.update(
        payload=payload,
        record_uuid=record_uuid,
        user=user,
    )

    try:
        updated = (
            sb.table("products")
            .select("name")
            .eq("uuid", record_uuid)
            .single()
            .execute()
            .data
        )

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

    record_uuid = f"test-delete-{uuid4()}"

    sb.table("products").insert({
        "uuid": record_uuid,
        "company_id": TEST_COMPANY_ID,
        "name": "Produto Delete",
        "sku": "SKU-DEL",
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
        row = (
            sb.table("products")
            .select("is_active")
            .eq("uuid", record_uuid)
            .single()
            .execute()
            .data
        )

        assert row["is_active"] is False
    finally:
        cleanup_product(record_uuid)
