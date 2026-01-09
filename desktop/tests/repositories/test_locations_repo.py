#desktop/tests/repositories/test_locations_repo.py

"""
Responsabilities:
- Unit tests for LocationsRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of locations data
"""

from desktop.data.repositories.locations_repo import LocationsRepo


def test_locations_create(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    uuid = repo.create({
        "code": "LOC-1",
        "name": "Armazém Central",
        "address": "Rua A",
    })

    row = conn_with_company.execute(
        """
        SELECT code, name, address, synced, source
        FROM locations_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == ("LOC-1", "Armazém Central", "Rua A", 0, "desktop")

    last_op = conn_with_company.execute(
        "SELECT operation FROM outbox_local ORDER BY id DESC LIMIT 1"
    ).fetchone()[0]

    assert last_op == "insert"


def test_locations_update(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    uuid = repo.create({
        "code": "LOC-1",
        "name": "Armazém",
    })

    repo.update(uuid, {"name": "Armazém Atualizado"})

    row = conn_with_company.execute(
        "SELECT name, synced FROM locations_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row == ("Armazém Atualizado", 0)


def test_locations_soft_delete(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    uuid = repo.create({
        "code": "LOC-1",
        "name": "Armazém",
    })

    repo.soft_delete(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM locations_local
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


def test_locations_restore(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    uuid = repo.create({
        "code": "LOC-1",
        "name": "Armazém",
    })

    repo.soft_delete(uuid)
    repo.restore(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM locations_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is None
    assert row[1] == 1
    assert row[2] == 0


def test_locations_get_all_active_only(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    uuid_active = repo.create({
        "code": "LOC-A",
        "name": "Ativo",
    })
    uuid_deleted = repo.create({
        "code": "LOC-D",
        "name": "Deletado",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted not in uuids


def test_locations_get_all_including_deleted(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    uuid_active = repo.create({
        "code": "LOC-A",
        "name": "Ativo",
    })
    uuid_deleted = repo.create({
        "code": "LOC-D",
        "name": "Deletado",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_locations_get_by_uuid(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    uuid = repo.create({
        "code": "LOC-1",
        "name": "Armazém",
    })

    repo.soft_delete(uuid)

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid
    assert row["deleted_at"] is not None


def test_locations_upsert_many(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 20,
            "company_server_id": 1,
            "code": "LOC-S",
            "name": "Local Server",
            "address": "Rua Server",
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT code, name, synced, source
        FROM locations_local
        WHERE uuid = 'u-1'
        """
    ).fetchone()

    assert row == ("LOC-S", "Local Server", 1, "server")


def test_locations_delete_all(conn_with_company):
    repo = LocationsRepo(conn_with_company)

    repo.create({
        "code": "LOC-1",
        "name": "Armazém",
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM locations_local"
    ).fetchone()[0]

    assert count == 0