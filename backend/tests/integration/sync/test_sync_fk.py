# backend/tests/integration/sync/test_sync_fk.py

"""
Responsibilities:
- Validate FK resolution rules for sync handlers.
"""

from uuid import uuid4

import pytest

from app.services.sync.handlers.inventory_event_targets import InventoryEventTargetSyncHandler
from tests.helpers.sync_data import (
    cleanup_by_uuid,
    create_event,
    create_location,
    create_product,
)


def test_inventory_event_targets_fk_validation(supabase, company_id, manager_user):
    handler = InventoryEventTargetSyncHandler()
    location = create_location(supabase, company_id)
    event = create_event(supabase, company_id, location_id=location["id"])
    product = create_product(supabase, company_id)
    record_uuid = str(uuid4())

    try:
        handler.insert(
            payload={
                "event_id": event["id"],
                "product_id": product["id"],
                "expected_qty": 5,
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        cleanup_by_uuid(supabase, "inventory_event_targets", record_uuid)

        with pytest.raises(RuntimeError) as excinfo:
            handler.insert(
                payload={
                    "event_id": event["id"],
                    "product_uuid": str(uuid4()),
                    "expected_qty": 5,
                },
                record_uuid=str(uuid4()),
                user=manager_user,
            )
        assert "FK_NOT_RESOLVED:products:product_id" in str(excinfo.value)
    finally:
        cleanup_by_uuid(supabase, "products", product["uuid"])
        cleanup_by_uuid(supabase, "inventory_events", event["uuid"])
        cleanup_by_uuid(supabase, "locations", location["uuid"])
