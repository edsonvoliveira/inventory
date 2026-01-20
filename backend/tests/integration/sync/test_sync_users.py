# backend/tests/integration/sync/test_sync_users.py

"""
Responsibilities:
- Validate users allowlist and invalid fields behavior.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.sync.handlers.users import UserSyncHandler
from tests.helpers.sync_data import create_user, cleanup_by_uuid


def test_users_update_allowlist(supabase, company_id, manager_user):
    handler = UserSyncHandler()
    record = create_user(supabase, company_id)
    record_uuid = record["uuid"]
    client_updated_at = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()

    try:
        handler.update(
            payload={
                "name": "User Updated",
                "role": "manager",
                "is_active": True,
                "client_updated_at": client_updated_at,
            },
            record_uuid=record_uuid,
            user=manager_user,
        )

        resp = (
            supabase.table("users")
            .select("name, role, is_active")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )
        row = resp.data[0]
        assert row["name"] == "User Updated"
        assert row["role"] == "manager"
        assert row["is_active"] is True
    finally:
        cleanup_by_uuid(supabase, "users", record_uuid)


def test_users_update_rejects_invalid_fields(supabase, company_id, manager_user):
    handler = UserSyncHandler()
    record = create_user(supabase, company_id)
    record_uuid = record["uuid"]
    client_updated_at = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()

    try:
        with pytest.raises(RuntimeError) as excinfo:
            handler.update(
                payload={
                    "email": "blocked@test.local",
                    "client_updated_at": client_updated_at,
                },
                record_uuid=record_uuid,
                user=manager_user,
            )
        assert "INVALID_FIELDS" in str(excinfo.value)
    finally:
        cleanup_by_uuid(supabase, "users", record_uuid)
