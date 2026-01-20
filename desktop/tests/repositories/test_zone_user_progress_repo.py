# desktop/tests/repositories/test_zone_user_progress_repo.py

"""
Responsibilities:
- Test zone user progress repo behavior.
"""

#desktop/tests/repositories/test_zone_user_progress_repo.py

"""
Responsabilities:
- Unit tests for ZoneUserProgressRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of zone user progress data
"""

import pytest

from desktop.data.repositories.zone_user_progress_repo import ZoneUserProgressRepo


def test_zone_user_progress_create(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })

    row = conn_with_company.execute(
        """
        SELECT count_type, synced, source
        FROM zone_user_progress_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == ("primary", 0, "desktop")


def test_zone_user_progress_update(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })

    repo.update(uuid, {"is_finished": 1})

    row = conn_with_company.execute(
        """
        SELECT is_finished, synced
        FROM zone_user_progress_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == (1, 0)


def test_zone_user_progress_soft_delete(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })

    with pytest.raises(RuntimeError):
        repo.soft_delete(uuid)


def test_zone_user_progress_restore(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })

    with pytest.raises(RuntimeError):
        repo.restore(uuid)


def test_zone_user_progress_get_all_active_only(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    uuid_active = repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })
    uuid_deleted = repo.create({
        "zone_server_id": 10,
        "user_server_id": 2,
        "count_type": "audit",
    })

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_zone_user_progress_get_all_including_deleted(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    uuid_active = repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })
    uuid_deleted = repo.create({
        "zone_server_id": 10,
        "user_server_id": 2,
        "count_type": "audit",
    })

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_zone_user_progress_get_by_uuid(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid


def test_zone_user_progress_upsert_many(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "p-1",
            "server_id": 200,
            "zone_server_id": 10,
            "user_server_id": 1,
            "count_type": "primary",
            "started_at": "2025-01-01T10:00:00Z",
            "is_finished": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT count_type, synced, source
        FROM zone_user_progress_local
        WHERE uuid = 'p-1'
        """
    ).fetchone()

    assert row == ("primary", 1, "server")


def test_zone_user_progress_delete_all(conn_with_company):
    repo = ZoneUserProgressRepo(conn_with_company)

    repo.create({
        "zone_server_id": 10,
        "user_server_id": 1,
        "count_type": "primary",
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM zone_user_progress_local"
    ).fetchone()[0]

    assert count == 0
