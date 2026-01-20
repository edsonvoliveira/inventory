# backend/tests/integration/sync/test_sync_devices.py

"""
Responsibilities:
- Validate devices allowlist and block rules.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.services.sync.handlers.devices import DeviceSyncHandler
from tests.helpers.sync_data import create_device, cleanup_by_uuid


def test_devices_rejects_is_blocked_on_insert(manager_user):
    handler = DeviceSyncHandler()
    record_uuid = str(uuid4())

    with pytest.raises(RuntimeError) as excinfo:
        handler.insert(
            payload={
                "device_uuid": f"device-{record_uuid[:8]}",
                "is_blocked": True,
            },
            record_uuid=record_uuid,
            user=manager_user,
        )
    assert "DEVICE_BLOCK_CHANGE_FORBIDDEN" in str(excinfo.value)


def test_devices_rejects_is_blocked_on_update(supabase, manager_user):
    handler = DeviceSyncHandler()
    device = create_device(
        supabase,
        user_id=manager_user.db_user_id,
        device_uuid=f"device-{uuid4().hex[:8]}",
        is_blocked=False,
    )

    try:
        with pytest.raises(RuntimeError) as excinfo:
            handler.update(
                payload={
                    "is_blocked": True,
                    "last_sync_at": datetime.now(timezone.utc).isoformat(),
                },
                record_uuid=device["uuid"],
                user=manager_user,
            )
        assert "DEVICE_BLOCK_CHANGE_FORBIDDEN" in str(excinfo.value)
    finally:
        cleanup_by_uuid(supabase, "devices", device["uuid"])
