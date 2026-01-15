# desktop/tests/repositories/test_outbox_repo.py

"""
Responsibilities:
- Test outbox repo behavior.
"""

#desktop/tests/repositories/test_outbox_repo.py

"""
Responsabilities:
- Unit tests for OutboxRepo
- Test CRUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of outbox messages
"""

from desktop.data.repositories.outbox_repo import OutboxRepo

def test_outbox_add_and_get_pending(conn_with_company):
    repo = OutboxRepo(conn_with_company)

    repo.add(
        table_name="products",
        operation="insert",
        record_uuid="u-1",
        payload={"name": "Produto"},
    )

    items = repo.get_pending()

    assert len(items) == 1
    item = items[0]

    assert item["table_name"] == "products"
    assert item["operation"] == "insert"
    assert item["record_uuid"] == "u-1"
    assert item["payload"]["name"] == "Produto"
    assert item["attempts"] == 0
    assert item["last_error"] is None


def test_outbox_mark_failed(conn_with_company):
    repo = OutboxRepo(conn_with_company)

    repo.add(
        table_name="products",
        operation="insert",
        record_uuid="u-1",
        payload={"name": "Produto"},
    )

    item = repo.get_pending()[0]
    repo.mark_failed(item["id"], "network error")

    row = conn_with_company.execute(
        """
        SELECT attempts, last_error
        FROM outbox_local
        WHERE id = ?
        """,
        (item["id"],),
    ).fetchone()

    assert row == (1, "network error")


def test_outbox_mark_success(conn_with_company):
    repo = OutboxRepo(conn_with_company)

    id1 = repo.add(
        table_name="products",
        operation="insert",
        record_uuid="u-1",
        payload={"name": "Produto"},
    )
    id2 = repo.add(
        table_name="products",
        operation="update",
        record_uuid="u-2",
        payload={"name": "Produto 2"},
    )

    repo.mark_success([id1])

    rows = conn_with_company.execute(
        "SELECT id FROM outbox_local ORDER BY id"
    ).fetchall()

    assert [r[0] for r in rows] == [id2]


def test_outbox_delete_all(conn_with_company):
    repo = OutboxRepo(conn_with_company)

    repo.add(
        table_name="products",
        operation="insert",
        record_uuid="u-1",
        payload={"name": "Produto"},
    )

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM outbox_local"
    ).fetchone()[0]

    assert count == 0