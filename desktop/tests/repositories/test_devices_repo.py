#desktop/tests/repositories/test_devices_repo.py

"""
Responsabilities:
- Unit tests for DevicesRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of devices data
"""

from desktop.data.repositories.devices_repo import DevicesRepo


def test_devices_upsert_many(conn_with_company):
    repo = DevicesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "d-1",
            "server_id": 10,
            "device_uuid": "device-uuid-1",
            "device_name": "Scanner 01",
            "os": "android",
            "app_version": "1.0.0",
            "is_blocked": 0,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT device_name, os, is_blocked, source
        FROM devices_local
        WHERE uuid = 'd-1'
        """
    ).fetchone()

    assert row == ("Scanner 01", "android", 0, "server")


def test_devices_soft_delete_from_server(conn_with_company):
    repo = DevicesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "d-1",
            "server_id": 10,
            "device_name": "Scanner 01",
            "is_blocked": 0,
            "source": "server",
        }
    ])

    repo.upsert_many([
        {
            "uuid": "d-1",
            "server_id": 10,
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT deleted_at
        FROM devices_local
        WHERE uuid = 'd-1'
        """
    ).fetchone()

    assert row[0] is not None


def test_devices_get_all_active_only(conn_with_company):
    repo = DevicesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "d-1",
            "server_id": 10,
            "device_name": "Ativo",
            "source": "server",
        },
        {
            "uuid": "d-2",
            "server_id": 11,
            "device_name": "Removido",
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        },
    ])

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert "d-1" in uuids
    assert "d-2" not in uuids


def test_devices_get_all_including_deleted(conn_with_company):
    repo = DevicesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "d-1",
            "server_id": 10,
            "device_name": "Ativo",
            "source": "server",
        },
        {
            "uuid": "d-2",
            "server_id": 11,
            "device_name": "Removido",
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        },
    ])

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert "d-1" in uuids
    assert "d-2" in uuids


def test_devices_get_by_uuid(conn_with_company):
    repo = DevicesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "d-1",
            "server_id": 10,
            "device_name": "Scanner",
            "os": "android",
            "source": "server",
        }
    ])

    row = repo.get_by_uuid("d-1")

    assert row is not None
    assert row["device_name"] == "Scanner"


def test_devices_delete_all(conn_with_company):
    repo = DevicesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "d-1",
            "server_id": 10,
            "device_name": "Scanner",
            "source": "server",
        }
    ])

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM devices_local"
    ).fetchone()[0]

    assert count == 0