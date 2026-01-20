# backend/tests/integration/sync/test_sync_finalized.py

"""
Responsibilities:
- Validate finalized event blocks writes (DB trigger).
"""

import pytest

from app.services.sync.handlers.zones import ZoneSyncHandler
from tests.helpers.sync_data import (
    cleanup_by_uuid,
    create_event,
    create_location,
    create_zone,
)


def test_finalized_event_blocks_zone_updates(supabase, company_id, manager_user):
    handler = ZoneSyncHandler()
    location = create_location(supabase, company_id)
    event = create_event(supabase, company_id, location_id=location["id"], status="open")
    zone = create_zone(supabase, event_id=event["id"])

    try:
        supabase.table("inventory_events").update(
            {"status": "finalized"}
        ).eq("uuid", event["uuid"]).execute()

        with pytest.raises(Exception):
            handler.update(
                payload={"name": "Zona Bloqueada", "client_updated_at": "2099-01-01T00:00:00Z"},
                record_uuid=zone["uuid"],
                user=manager_user,
            )
    finally:
        supabase.table("inventory_events").update(
            {"status": "open"}
        ).eq("uuid", event["uuid"]).execute()
        cleanup_by_uuid(supabase, "zones", zone["uuid"])
        cleanup_by_uuid(supabase, "inventory_events", event["uuid"])
        cleanup_by_uuid(supabase, "locations", location["uuid"])
