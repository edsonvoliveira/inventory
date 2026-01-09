#desktop/tests/repositories/test_product_categories_repo.py

"""
Responsabilities:
- Unit tests for ProductCategoriesRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of product categories data
"""

from desktop.data.repositories.product_categories_repo import ProductCategoriesRepo

def test_product_categories_create(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    uuid = repo.create({
        "code": "CAT-1",
        "name": "Categoria Teste",
        "description": "Descrição",
    })

    row = conn_with_company.execute(
        """
        SELECT code, name, description, synced, source
        FROM product_categories_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row == ("CAT-1", "Categoria Teste", "Descrição", 0, "desktop")

    ops = [
        r[0]
        for r in conn_with_company.execute(
            "SELECT operation FROM outbox_local ORDER BY id"
        )
    ]
    assert ops[-1] == "insert"


def test_product_categories_update(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    uuid = repo.create({
        "code": "CAT-1",
        "name": "Categoria",
    })

    repo.update(uuid, {"name": "Categoria Atualizada"})

    row = conn_with_company.execute(
        "SELECT name, synced FROM product_categories_local WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    assert row == ("Categoria Atualizada", 0)


def test_product_categories_soft_delete(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    uuid = repo.create({
        "code": "CAT-1",
        "name": "Categoria",
    })

    repo.soft_delete(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM product_categories_local
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


def test_product_categories_restore(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    uuid = repo.create({
        "code": "CAT-1",
        "name": "Categoria",
    })

    repo.soft_delete(uuid)
    repo.restore(uuid)

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active, synced
        FROM product_categories_local
        WHERE uuid = ?
        """,
        (uuid,),
    ).fetchone()

    assert row[0] is None
    assert row[1] == 1
    assert row[2] == 0


def test_product_categories_get_all_active_only(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    uuid_active = repo.create({
        "code": "CAT-A",
        "name": "Ativa",
    })
    uuid_deleted = repo.create({
        "code": "CAT-D",
        "name": "Deletada",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all()
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted not in uuids


def test_product_categories_get_all_including_deleted(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    uuid_active = repo.create({
        "code": "CAT-A",
        "name": "Ativa",
    })
    uuid_deleted = repo.create({
        "code": "CAT-D",
        "name": "Deletada",
    })

    repo.soft_delete(uuid_deleted)

    rows = repo.get_all(active_only=False)
    uuids = {r["uuid"] for r in rows}

    assert uuid_active in uuids
    assert uuid_deleted in uuids


def test_product_categories_get_by_uuid(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    uuid = repo.create({
        "code": "CAT-1",
        "name": "Categoria",
    })

    repo.soft_delete(uuid)

    row = repo.get_by_uuid(uuid)

    assert row is not None
    assert row["uuid"] == uuid
    assert row["deleted_at"] is not None


def test_product_categories_upsert_many(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "company_server_id": 1,
            "code": "CAT-S",
            "name": "Categoria Server",
            "description": "Origem server",
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT code, name, synced, source
        FROM product_categories_local
        WHERE uuid = 'u-1'
        """
    ).fetchone()

    assert row == ("CAT-S", "Categoria Server", 1, "server")


def test_product_categories_delete_all(conn_with_company):
    repo = ProductCategoriesRepo(conn_with_company)

    repo.create({
        "code": "CAT-1",
        "name": "Categoria",
    })

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM product_categories_local"
    ).fetchone()[0]

    assert count == 0
