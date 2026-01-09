#desktop/tests/repositories/test_product_barcodes_repo.py

"""
Responsabilities:
- Unit tests for ProductBarcodesRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of product_barcodes data
"""

from desktop.data.repositories.product_barcodes_repo import ProductBarcodesRepo


def test_product_barcodes_create(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    uuid = repo.create({
        "product_server_id": 10,
        "barcode": "7890001112223",
        "description": "EAN principal",
    })

    row = conn_with_company.execute(
        """
        SELECT barcode, description, synced, source
        FROM product_barcodes_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == ("7890001112223", "EAN principal", 0, "desktop")


def test_product_barcodes_update(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    uuid = repo.create({
        "product_server_id": 10,
        "barcode": "7890001112223",
        "description": "EAN",
    })

    repo.update(uuid, {"description": "EAN atualizado"})

    row = conn_with_company.execute(
        """
        SELECT description, synced
        FROM product_barcodes_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == ("EAN atualizado", 0)


def test_product_barcodes_soft_delete(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    uuid = repo.create({
        "product_server_id": 10,
        "barcode": "7890001112223",
    })

    repo.soft_delete(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM product_barcodes_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is not None
    assert row[1] == 0
    assert row[2] == 0


def test_product_barcodes_restore(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    uuid = repo.create({
        "product_server_id": 10,
        "barcode": "7890001112223",
    })

    repo.soft_delete(uuid)
    repo.restore(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM product_barcodes_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is None
    assert row[1] == 1
    assert row[2] == 0


def test_product_barcodes_get_all_active_only(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    uuid_active = repo.create({
        "product_server_id": 10,
        "barcode": "111",
    })
    uuid_deleted = repo.create({
        "product_server_id": 10,
        "barcode": "222",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted not in uuids


def test_product_barcodes_get_all_including_deleted(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    uuid_active = repo.create({
        "product_server_id": 10,
        "barcode": "111",
    })
    uuid_deleted = repo.create({
        "product_server_id": 10,
        "barcode": "222",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_product_barcodes_get_by_uuid(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    uuid = repo.create({
        "product_server_id": 10,
        "barcode": "7890001112223",
    })

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid
    assert row["barcode"] == "7890001112223"


def test_product_barcodes_upsert_many(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "b-1",
            "server_id": 50,
            "company_server_id": 1,
            "product_server_id": 10,
            "barcode": "999",
            "description": "Barcode server",
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT barcode, synced, source
        FROM product_barcodes_local
        WHERE uuid = 'b-1'
        """
    ).fetchone()

    assert row == ("999", 1, "server")


def test_product_barcodes_delete_all(conn_with_company):
    repo = ProductBarcodesRepo(conn_with_company)

    repo.create({
        "product_server_id": 10,
        "barcode": "7890001112223",
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM product_barcodes_local"
    ).fetchone()[0]

    assert count == 0