#desktop/tests/repositories/test_inventory_event_targets_repo.py

"""
Responsabilities:
- Unit tests for InventoryEventTargetsRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of inventory event targets data
"""

from desktop.data.repositories.inventory_event_targets_repo import InventoryEventTargetsRepo

def test_inventory_event_targets_create(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })

    row = conn_with_company.execute(
        """
        SELECT expected_qty, synced, source
        FROM inventory_event_targets_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == (10, 0, "desktop")


def test_inventory_event_targets_update(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })

    repo.update(uuid, {"expected_qty": 20})

    row = conn_with_company.execute(
        "SELECT expected_qty, synced FROM inventory_event_targets_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row == (20, 0)


def test_inventory_event_targets_soft_delete(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })

    repo.soft_delete(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM inventory_event_targets_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is not None
    assert row[1] == 0
    assert row[2] == 0


def test_inventory_event_targets_restore(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })

    repo.soft_delete(uuid)
    repo.restore(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM inventory_event_targets_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is None
    assert row[1] == 1
    assert row[2] == 0


def test_inventory_event_targets_get_all_active_only(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    uuid_active = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })
    uuid_deleted = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 5,
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted not in uuids


def test_inventory_event_targets_get_all_including_deleted(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    uuid_active = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })
    uuid_deleted = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 5,
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_inventory_event_targets_get_by_uuid(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    uuid = repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })

    repo.soft_delete(uuid)

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid
    assert row["deleted_at"] is not None


def test_inventory_event_targets_upsert_many(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "t-1",
            "server_id": 60,
            "company_server_id": 1,
            "event_server_id": 100,
            "product_server_id": 200,
            "expected_qty": 20,
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT expected_qty, synced, source
        FROM inventory_event_targets_local
        WHERE uuid = 't-1'
        """
    ).fetchone()

    assert row == (20, 1, "server")


def test_inventory_event_targets_delete_all(conn_with_company):
    repo = InventoryEventTargetsRepo(conn_with_company)

    repo.create({
        "event_server_id": 100,
        "product_server_id": 200,
        "expected_qty": 10,
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM inventory_event_targets_local"
    ).fetchone()[0]

    assert count == 0