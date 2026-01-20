# backend/tests/integration/sync/test_sync_orchestrator.py

"""
Responsibilities:
- Validate push orchestration rules (origin and device block).
"""

from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.sync import SyncItem
from app.services.sync.push_orchestrator import PushOrchestrator
from tests.helpers.sync_data import create_device, create_product, create_user, cleanup_by_uuid


def test_push_origin_enforcement(counter_user):
    item = SyncItem(
        table_name="products",
        operation="update",
        record_uuid=str(uuid4()),
        payload={
            "name": "Nao permitido",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    accepted, failed, rejected, _server_ids = PushOrchestrator().run([item], counter_user, origin="mobile")
    assert item.record_uuid in failed
    assert rejected.get(item.record_uuid) == "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
    assert accepted == []


def test_push_device_blocked(supabase, manager_user):
    device = create_device(
        supabase,
        user_id=manager_user.db_user_id,
        device_uuid="device-blocked",
        is_blocked=True,
    )

    item = SyncItem(
        table_name="devices",
        operation="update",
        record_uuid=str(uuid4()),
        payload={
            "device_uuid": "device-blocked",
            "last_sync_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    try:
        accepted, failed, rejected, _server_ids = PushOrchestrator().run([item], manager_user)
        assert item.record_uuid in failed
        assert rejected.get(item.record_uuid) == "DEVICE_BLOCKED"
        assert accepted == []
    finally:
        cleanup_by_uuid(supabase, "devices", device["uuid"])


def test_desktop_admin_allows_users_update(supabase, company_id, admin_user):
    record = create_user(supabase, company_id)
    record_uuid = record["uuid"]

    item = SyncItem(
        table_name="users",
        operation="update",
        record_uuid=record_uuid,
        payload={
            "name": "User Updated",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    try:
        accepted, failed, rejected, _server_ids = PushOrchestrator().run(
            [item],
            admin_user,
            origin="desktop",
        )
        assert record_uuid in accepted
        assert record_uuid not in failed
        assert rejected == {}
    finally:
        cleanup_by_uuid(supabase, "users", record_uuid)


def test_desktop_manager_rejects_users_update(manager_user):
    item = SyncItem(
        table_name="users",
        operation="update",
        record_uuid=str(uuid4()),
        payload={
            "name": "Not allowed",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    accepted, failed, rejected, _server_ids = PushOrchestrator().run(
        [item],
        manager_user,
        origin="desktop",
    )
    assert item.record_uuid in failed
    assert rejected.get(item.record_uuid) == "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
    assert accepted == []


def test_desktop_admin_rejects_companies_update(admin_user):
    item = SyncItem(
        table_name="companies",
        operation="update",
        record_uuid=str(uuid4()),
        payload={
            "name": "Not allowed",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    accepted, failed, rejected, _server_ids = PushOrchestrator().run(
        [item],
        admin_user,
        origin="desktop",
    )
    assert item.record_uuid in failed
    assert rejected.get(item.record_uuid) == "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
    assert accepted == []


def test_desktop_manager_allows_products_update(supabase, company_id, manager_user):
    record = create_product(supabase, company_id)
    record_uuid = record["uuid"]

    item = SyncItem(
        table_name="products",
        operation="update",
        record_uuid=record_uuid,
        payload={
            "name": "Produto Atualizado",
            "client_updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    try:
        accepted, failed, rejected, _server_ids = PushOrchestrator().run(
            [item],
            manager_user,
            origin="desktop",
        )
        assert record_uuid in accepted
        assert record_uuid not in failed
        assert rejected == {}
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)


def test_mobile_counter_allows_devices_insert(supabase, counter_user):
    record_uuid = str(uuid4())
    device_uuid = f"device-{record_uuid[:8]}"

    item = SyncItem(
        table_name="devices",
        operation="insert",
        record_uuid=record_uuid,
        payload={
            "device_uuid": device_uuid,
            "os": "android",
            "app_version": "1.0.0",
        },
    )

    try:
        accepted, failed, rejected, _server_ids = PushOrchestrator().run(
            [item],
            counter_user,
            origin="mobile",
        )
        assert record_uuid in accepted
        assert record_uuid not in failed
        assert rejected == {}
    finally:
        cleanup_by_uuid(supabase, "devices", record_uuid)
