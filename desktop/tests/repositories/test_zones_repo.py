# desktop/tests/repositories/test_zones_repo.py

"""
Responsibilities:
- Test zones repo behavior.
"""

#desktop/tests/repositories/test_zones_repo.py

"""
Responsabilities:
- Unit tests for ZonesRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of zones data
"""

from desktop.data.repositories.zones_repo import ZonesRepo


def test_zones_create(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "name": "Zona A",
        "description": "Zona principal",
    })

    row = conn_with_company.execute(
        """
        SELECT event_server_id, name, description, synced, source
        FROM zones_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == (100, "Zona A", "Zona principal", 0, "desktop")

    last_op = conn_with_company.execute(
        "SELECT operation FROM outbox_local ORDER BY id DESC LIMIT 1"
    ).fetchone()[0]

    assert last_op == "insert"


def test_zones_update(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "name": "Zona A",
    })

    repo.update(uuid, {"name": "Zona Atualizada"})

    row = conn_with_company.execute(
        "SELECT name, synced FROM zones_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row == ("Zona Atualizada", 0)


def test_zones_soft_delete(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "name": "Zona A",
    })

    repo.soft_delete(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM zones_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is not None
    assert row[1] == 0
    assert row[2] == 0

    last_op = conn_with_company.execute(
        "SELECT operation FROM outbox_local ORDER BY id DESC LIMIT 1"
    ).fetchone()[0]

    assert last_op == "delete"


def test_zones_restore(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "name": "Zona A",
    })

    repo.soft_delete(uuid)
    repo.restore(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM zones_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is None
    assert row[1] == 1
    assert row[2] == 0


def test_zones_get_all_active_only(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    uuid_active = repo.create({
        "event_server_id": 100,
        "name": "Ativa",
    })
    uuid_deleted = repo.create({
        "event_server_id": 100,
        "name": "Deletada",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted not in uuids


def test_zones_get_all_including_deleted(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    uuid_active = repo.create({
        "event_server_id": 100,
        "name": "Ativa",
    })
    uuid_deleted = repo.create({
        "event_server_id": 100,
        "name": "Deletada",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_zones_get_by_uuid(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "name": "Zona A",
    })

    repo.soft_delete(uuid)

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid
    assert row["deleted_at"] is not None


def test_zones_upsert_many(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 30,
            "event_server_id": 100,
            "name": "Zona Server",
            "description": "Origem server",
            "count_status": "open",
            "lock_status": "unlocked",
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT name, synced, source
        FROM zones_local
        WHERE uuid = 'u-1'
        """
    ).fetchone()

    assert row == ("Zona Server", 1, "server")


def test_zones_delete_all(conn_with_company):
    repo = ZonesRepo(conn_with_company)

    repo.create({
        "event_server_id": 100,
        "name": "Zona A",
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM zones_local"
    ).fetchone()[0]

    assert count == 0