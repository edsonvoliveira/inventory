# backend/tests/integration/sync/test_sync_pending_contract.py

"""
Responsibilities:
- Contract rules pending backend enforcement (xfail).
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.services.sync.handlers.inventory_events import InventoryEventSyncHandler
from app.services.sync.handlers.zones import ZoneSyncHandler
from tests.helpers.sync_data import (
    cleanup_by_uuid,
    create_event,
    create_location,
    create_zone,
)


def test_zone_close_requires_required_counts(supabase, company_id, manager_user):
    location = create_location(supabase, company_id)
    event = create_event(supabase, company_id, location_id=location["id"], required_counts=2)
    zone = create_zone(supabase, event_id=event["id"])
    handler = ZoneSyncHandler()

    try:
        with pytest.raises(RuntimeError):
            handler.update(
                payload={
                    "count_status": "finished",
                    "client_updated_at": datetime.now(timezone.utc).isoformat(),
                },
                record_uuid=zone["uuid"],
                user=manager_user,
            )
    finally:
        cleanup_by_uuid(supabase, "zones", zone["uuid"])
        cleanup_by_uuid(supabase, "inventory_events", event["uuid"])
        cleanup_by_uuid(supabase, "locations", location["uuid"])


def test_event_close_requires_zones_finished(supabase, company_id, manager_user):
    location = create_location(supabase, company_id)
    event = create_event(supabase, company_id, location_id=location["id"])
    create_zone(supabase, event_id=event["id"])
    handler = InventoryEventSyncHandler()

    try:
        with pytest.raises(RuntimeError):
            handler.update(
                payload={
                    "status": "closed",
                    "client_updated_at": datetime.now(timezone.utc).isoformat(),
                },
                record_uuid=event["uuid"],
                user=manager_user,
            )
    finally:
        cleanup_by_uuid(supabase, "inventory_events", event["uuid"])
        cleanup_by_uuid(supabase, "locations", location["uuid"])
