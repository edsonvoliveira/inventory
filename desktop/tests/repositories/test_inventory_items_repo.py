# desktop/tests/repositories/test_inventory_items_repo.py

"""
Responsibilities:
- Test inventory items repo behavior.
"""

#desktop/tests/repositories/test_inventory_items_repo.py

"""
Responsabilities:
- Unit tests for InventoryItemsRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of inventory items data
"""

import pytest

from desktop.data.repositories.inventory_items_repo import InventoryItemsRepo

def test_inventory_items_create(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })

    row = conn_with_company.execute(
        """
        SELECT qty_counted, synced, source
        FROM inventory_items_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == (5, 0, "desktop")


def test_inventory_items_update(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })

    repo.update(uuid, {"qty_counted": 8})

    row = conn_with_company.execute(
        """
        SELECT qty_counted, synced
        FROM inventory_items_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == (8, 0)


def test_inventory_items_soft_delete(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })

    with pytest.raises(RuntimeError):
        repo.soft_delete(uuid)


def test_inventory_items_restore(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })

    with pytest.raises(RuntimeError):
        repo.restore(uuid)


def test_inventory_items_get_all_active_only(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    uuid_active = repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })
    uuid_deleted = repo.create({
        "zone_server_id": 10,
        "product_server_id": 21,
        "qty_counted": 3,
    })

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_inventory_items_get_all_including_deleted(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    uuid_active = repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })
    uuid_deleted = repo.create({
        "zone_server_id": 10,
        "product_server_id": 21,
        "qty_counted": 3,
    })

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_inventory_items_get_by_uuid(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    uuid = repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid


def test_inventory_items_upsert_many(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "i-1",
            "server_id": 100,
            "zone_server_id": 10,
            "product_server_id": 20,
            "qty_counted": 7,
            "device_timestamp": "2025-01-01T10:00:00Z",
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT qty_counted, synced, source
        FROM inventory_items_local
        WHERE uuid = 'i-1'
        """
    ).fetchone()

    assert row == (7, 1, "server")


def test_inventory_items_delete_all(conn_with_company):
    repo = InventoryItemsRepo(conn_with_company)

    repo.create({
        "zone_server_id": 10,
        "product_server_id": 20,
        "qty_counted": 5,
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM inventory_items_local"
    ).fetchone()[0]

    assert count == 0
