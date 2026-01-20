# backend/tests/integration/sync/test_sync_items_progress.py

"""
Responsibilities:
- Validate inventory_items and zone_user_progress handlers.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.services.sync.handlers.inventory_items import InventoryItemSyncHandler
from app.services.sync.handlers.zone_user_progress import ZoneUserProgressHandler
from tests.helpers.sync_data import (
    cleanup_by_uuid,
    create_event,
    create_location,
    create_product,
    create_user,
    create_zone,
)


def test_inventory_items_insert_update_and_delete_blocked(supabase, company_id, manager_user):
    handler = InventoryItemSyncHandler()
    location = create_location(supabase, company_id)
    event = create_event(supabase, company_id, location_id=location["id"])
    zone = create_zone(supabase, event_id=event["id"])
    product = create_product(supabase, company_id)
    record_uuid = str(uuid4())

    try:
        handler.insert(
            payload={
                "zone_id": zone["id"],
                "product_id": product["id"],
                "user_id": manager_user.db_user_id,
                "qty_counted": 3,
                "device_timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "mobile",
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        future_ts = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
        handler.update(
            payload={
                "qty_counted": 5,
                "client_updated_at": future_ts,
                "user_id": manager_user.db_user_id,
                "device_timestamp": datetime.now(timezone.utc).isoformat(),
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        with pytest.raises(RuntimeError) as excinfo:
            handler.delete(payload={}, record_uuid=record_uuid, user=manager_user)
        assert "inventory_items nao suportam delete via sync" in str(excinfo.value)
    finally:
        # inventory_items geram inventory_item_events (append-only),
        # entao evitamos deletar itens/zonas/eventos para nao quebrar triggers.
        cleanup_by_uuid(supabase, "products", product["uuid"])


def test_zone_user_progress_insert_update_and_validation(supabase, company_id, manager_user):
    handler = ZoneUserProgressHandler()
    location = create_location(supabase, company_id)
    event = create_event(supabase, company_id, location_id=location["id"])
    zone = create_zone(supabase, event_id=event["id"])
    user_row = create_user(supabase, company_id)
    record_uuid = str(uuid4())

    try:
        handler.insert(
            payload={
                "zone_id": zone["id"],
                "user_id": user_row["id"],
                "count_type": "primary",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "device_id": "device-test",
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        handler.update(
            payload={
                "items_counted": 10,
                "qty_total": 10,
                "is_finished": True,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "client_updated_at": datetime.now(timezone.utc).isoformat(),
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        with pytest.raises(RuntimeError) as excinfo:
            handler.insert(
                payload={
                    "zone_id": zone["id"],
                    "user_id": user_row["id"],
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "device_id": "device-test",
                },
                record_uuid=str(uuid4()),
                user=manager_user,
            )
        assert "count_type ausente" in str(excinfo.value)
    finally:
        cleanup_by_uuid(supabase, "zone_user_progress", record_uuid)
        cleanup_by_uuid(supabase, "users", user_row["uuid"])
        cleanup_by_uuid(supabase, "zones", zone["uuid"])
        cleanup_by_uuid(supabase, "inventory_events", event["uuid"])
        cleanup_by_uuid(supabase, "locations", location["uuid"])
