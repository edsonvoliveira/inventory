# desktop/tests/repositories/test_inventory_events_repo.py

"""
Responsibilities:
- Test inventory events repo behavior.
"""

#desktop/tests/repositories/test_inventory_events_repo.py

"""
Responsabilities:
- Unit tests for InventoryEventsRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of inventory events data
"""

from desktop.data.repositories.inventory_events_repo import InventoryEventsRepo

def test_inventory_events_create(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    uuid = repo.create({
        "location_server_id": 10,
        "title": "Inventário Geral",
        "status": "open",
    })

    row = conn_with_company.execute(
        """
        SELECT title, status, synced, source
        FROM inventory_events_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == ("Inventário Geral", "open", 0, "desktop")


def test_inventory_events_update(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    uuid = repo.create({
        "location_server_id": 10,
        "title": "Inventário",
        "status": "open",
    })

    repo.update(uuid, {"status": "closed"})

    row = conn_with_company.execute(
        "SELECT status, synced FROM inventory_events_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row == ("closed", 0)


def test_inventory_events_soft_delete(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    uuid = repo.create({
        "location_server_id": 10,
        "title": "Inventário",
        "status": "open",
    })

    repo.soft_delete(uuid)

    row = conn_with_company.execute(
        """
        SELECT is_active, synced
        FROM inventory_events_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] == 0
    assert row[1] == 0


def test_inventory_events_restore(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    uuid = repo.create({
        "location_server_id": 10,
        "title": "Inventário",
        "status": "open",
    })

    repo.soft_delete(uuid)
    repo.restore(uuid)

    row = conn_with_company.execute(
        """
        SELECT is_active, synced
        FROM inventory_events_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] == 1
    assert row[1] == 0


def test_inventory_events_get_all_active_only(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    uuid_active = repo.create({
        "location_server_id": 10,
        "title": "Ativo",
        "status": "open",
    })
    uuid_deleted = repo.create({
        "location_server_id": 10,
        "title": "Deletado",
        "status": "open",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted not in uuids


def test_inventory_events_get_all_including_deleted(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    uuid_active = repo.create({
        "location_server_id": 10,
        "title": "Ativo",
        "status": "open",
    })
    uuid_deleted = repo.create({
        "location_server_id": 10,
        "title": "Deletado",
        "status": "open",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_inventory_events_get_by_uuid(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    uuid = repo.create({
        "location_server_id": 10,
        "title": "Inventário",
        "status": "open",
    })

    repo.soft_delete(uuid)

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid
    assert row["is_active"] == 0


def test_inventory_events_upsert_many(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "e-1",
            "server_id": 50,
            "company_server_id": 1,
            "location_server_id": 10,
            "title": "Evento Server",
            "status": "closed",
            "required_counts": 1,
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT title, status, synced, source
        FROM inventory_events_local
        WHERE uuid = 'e-1'
        """
    ).fetchone()

    assert row == ("Evento Server", "closed", 1, "server")


def test_inventory_events_delete_all(conn_with_company):
    repo = InventoryEventsRepo(conn_with_company)

    repo.create({
        "location_server_id": 10,
        "title": "Inventário",
        "status": "open",
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM inventory_events_local"
    ).fetchone()[0]

    assert count == 0
