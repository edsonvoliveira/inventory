# backend/tests/integration/sync/test_sync_catalog.py

"""
Responsibilities:
- Validate product_categories, locations, and product_barcodes handlers.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.services.sync.handlers.locations import LocationSyncHandler
from app.services.sync.handlers.product_barcodes import ProductBarcodeSyncHandler
from app.services.sync.handlers.product_categories import ProductCategorySyncHandler
from tests.helpers.sync_data import (
    cleanup_by_uuid,
    create_product,
)


def test_product_categories_allowlist(supabase, company_id, manager_user):
    handler = ProductCategorySyncHandler()
    record_uuid = str(uuid4())

    try:
        handler.insert(
            payload={"code": f"CAT-{record_uuid[:8]}", "name": "Categoria"},
            record_uuid=record_uuid,
            user=manager_user,
        )

        handler.update(
            payload={
                "name": "Categoria Atualizada",
                "client_updated_at": datetime.now(timezone.utc).isoformat(),
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        with pytest.raises(RuntimeError) as excinfo:
            handler.update(
                payload={"unknown": "x", "client_updated_at": datetime.now(timezone.utc).isoformat()},
                record_uuid=record_uuid,
                user=manager_user,
            )
        assert "INVALID_FIELDS" in str(excinfo.value)
    finally:
        cleanup_by_uuid(supabase, "product_categories", record_uuid)


def test_locations_allowlist(supabase, company_id, manager_user):
    handler = LocationSyncHandler()
    record_uuid = str(uuid4())

    try:
        handler.insert(
            payload={"name": "Local 1"},
            record_uuid=record_uuid,
            user=manager_user,
        )

        handler.update(
            payload={
                "address": "Rua 1",
                "client_updated_at": datetime.now(timezone.utc).isoformat(),
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        with pytest.raises(RuntimeError) as excinfo:
            handler.update(
                payload={"unknown": "x", "client_updated_at": datetime.now(timezone.utc).isoformat()},
                record_uuid=record_uuid,
                user=manager_user,
            )
        assert "INVALID_FIELDS" in str(excinfo.value)
    finally:
        cleanup_by_uuid(supabase, "locations", record_uuid)


def test_product_barcodes_fk_and_allowlist(supabase, company_id, manager_user):
    handler = ProductBarcodeSyncHandler()
    product = create_product(supabase, company_id)
    record_uuid = str(uuid4())

    try:
        handler.insert(
            payload={
                "product_id": product["id"],
                "barcode": f"BC-{record_uuid[:8]}",
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        handler.update(
            payload={
                "description": "Atualizado",
                "client_updated_at": datetime.now(timezone.utc).isoformat(),
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        with pytest.raises(RuntimeError) as excinfo:
            handler.update(
                payload={"unknown": "x", "client_updated_at": datetime.now(timezone.utc).isoformat()},
                record_uuid=record_uuid,
                user=manager_user,
            )
        assert "INVALID_FIELDS" in str(excinfo.value)
    finally:
        cleanup_by_uuid(supabase, "product_barcodes", record_uuid)
        cleanup_by_uuid(supabase, "products", product["uuid"])
