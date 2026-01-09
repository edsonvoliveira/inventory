#desktop/tests/repositories/test_products_repo.py
"""
Responsabilities:
- Tests for ProductsRepo CRUD operations
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of product data
"""

from desktop.data.repositories.conftest import conn_with_company
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.tests.helpers.db import make_test_connection

def test_products_create(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    uuid = repo.create({
        "sku": "SKU-1",
        "name": "Produto Teste",
    })

    row = conn_with_company.execute(
        "SELECT sku, name, synced, source FROM products_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row == ("SKU-1", "Produto Teste", 0, "desktop")

    outbox = conn_with_company.execute("SELECT operation FROM outbox_local").fetchone()
    assert outbox[0] == "insert"

def test_products_update(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    uuid = repo.create({"sku": "SKU-1", "name": "Produto"})
    repo.update(uuid, {"name": "Produto Atualizado"})

    row = conn_with_company.execute(
        "SELECT name, synced FROM products_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row == ("Produto Atualizado", 0)

    ops = [r[0] for r in conn_with_company.execute("SELECT operation FROM outbox_local")]
    assert ops == ["insert", "update"]

def test_products_soft_delete(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    uuid = repo.create({"sku": "SKU-1", "name": "Produto"})
    repo.soft_delete(uuid)

    row = conn_with_company.execute(
        "SELECT deleted_at, is_active, synced FROM products_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row[0] is not None
    assert row[1] == 0
    assert row[2] == 0

    ops = [r[0] for r in conn_with_company.execute("SELECT operation FROM outbox_local ORDER BY id")]
    assert ops[-1] == "delete"

def test_products_restore(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    uuid = repo.create({"sku": "SKU-1", "name": "Produto"})
    repo.soft_delete(uuid)
    repo.restore(uuid)

    row = conn_with_company.execute(
        "SELECT deleted_at, is_active, synced FROM products_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row[0] is None
    assert row[1] == 1
    assert row[2] == 0

def test_products_get_all_active_only(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    uuid_active = repo.create({"sku": "SKU-1", "name": "Produto Ativo"})
    uuid_deleted = repo.create({"sku": "SKU-2", "name": "Produto Deletado"})

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all()

    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted not in uuids

def test_products_get_all_including_deleted(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    uuid_active = repo.create({"sku": "SKU-1", "name": "Produto Ativo"})
    uuid_deleted = repo.create({"sku": "SKU-2", "name": "Produto Deletado"})

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all(active_only=False)

    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids

def test_products_get_by_uuid(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    uuid = repo.create({"sku": "SKU-1", "name": "Produto Teste"})
    repo.soft_delete(uuid)

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid
    assert row["deleted_at"] is not None

def test_products_upsert_many(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "company_server_id": 1,
            "sku": "SKU-1",
            "name": "Produto Server",
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        "SELECT server_id, name, synced, source FROM products_local WHERE uuid = 'u-1'"
    ).fetchone()

    assert row == (10, "Produto Server", 1, "server")
    assert conn_with_company.execute("SELECT COUNT(*) FROM outbox_local").fetchone()[0] == 0

def test_products_delete_all(conn_with_company):
    repo = ProductsRepo(conn_with_company)

    repo.create({"sku": "SKU-1", "name": "Produto"})
    repo.delete_all()

    count = conn_with_company.execute("SELECT COUNT(*) FROM products_local").fetchone()[0]
    assert count == 0
