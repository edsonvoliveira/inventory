# backend/tests/integration/sync/test_sync_products.py

"""
Responsibilities:
- Validate products LWW and idempotent insert behavior.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.services.sync.handlers.products import ProductSyncHandler
from tests.helpers.sync_data import create_product, cleanup_by_uuid


def test_products_idempotent_insert(supabase, company_id, manager_user):
    handler = ProductSyncHandler()
    record_uuid = str(uuid4())

    payload = {
        "name": "Produto Idempotente",
        "sku": f"SKU-{record_uuid[:8]}",
        "uom_base": "UN",
        "uom_inventory": "UN",
        "is_active": True,
    }

    handler.insert(payload=payload, record_uuid=record_uuid, user=manager_user)
    handler.insert(payload=payload, record_uuid=record_uuid, user=manager_user)

    try:
        resp = (
            supabase.table("products")
            .select("uuid")
            .eq("uuid", record_uuid)
            .execute()
        )
        assert isinstance(resp.data, list)
        assert len(resp.data) == 1
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)


def test_products_lww_update(supabase, company_id, manager_user):
    handler = ProductSyncHandler()
    record = create_product(supabase, company_id, name="Produto Original")
    record_uuid = record["uuid"]

    try:
        past_ts = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        handler.update(
            payload={
                "name": "Produto Antigo",
                "client_updated_at": past_ts,
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        resp = (
            supabase.table("products")
            .select("name")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )
        row = resp.data[0]
        assert row["name"] == "Produto Original"

        future_ts = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
        handler.update(
            payload={
                "name": "Produto Novo",
                "client_updated_at": future_ts,
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        resp = (
            supabase.table("products")
            .select("name")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )
        row = resp.data[0]
        assert row["name"] == "Produto Novo"
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)


def test_products_lww_update_equal_timestamp_noop(supabase, company_id, manager_user):
    handler = ProductSyncHandler()
    record = create_product(supabase, company_id, name="Produto Original")
    record_uuid = record["uuid"]

    try:
        resp = (
            supabase.table("products")
            .select("name, updated_at")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )
        row = resp.data[0]
        server_updated_at = row["updated_at"]

        handler.update(
            payload={
                "name": "Produto Igual",
                "client_updated_at": server_updated_at,
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        resp = (
            supabase.table("products")
            .select("name")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )
        row = resp.data[0]
        assert row["name"] == "Produto Original"
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)
