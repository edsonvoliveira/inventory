# desktop/tests/core/sync/test_apply_pull_payload.py

"""
Responsibilities:
- Test apply pull payload behavior.
"""

#desktop/tests/core/sync/test_apply_pull_payload.py

from desktop.core.sync.apply_pull_payload import apply_pull_payload


def test_apply_pull_payload_products(conn_with_company):
    payload = {
        "products": [
            {
                "uuid": "p-1",
                "server_id": 10,
                "company_server_id": 1,
                "sku": "SKU-1",
                "name": "Produto Server",
                "is_active": 1,
                "synced": 1,
                "source": "server",
            }
        ],
        "server_ts": "2026-01-10T10:30:00Z",
    }

    apply_pull_payload(payload, conn_with_company)

    row = conn_with_company.execute(
        """
        SELECT name, source
        FROM products_local
        WHERE uuid = 'p-1'
        """
    ).fetchone()

    assert row == ("Produto Server", "server")

    meta = conn_with_company.execute(
        "SELECT value FROM app_meta WHERE key = 'last_pull_at'"
    ).fetchone()

    assert meta[0] == "2026-01-10T10:30:00Z"

def test_apply_pull_payload_multiple_entities(conn_with_company):
    payload = {
        "product_categories": [
            {
                "uuid": "c-1",
                "server_id": 5,
                "company_server_id": 1,
                "code": "CAT",
                "name": "Categoria",
                "is_active": 1,
                "synced": 1,
                "source": "server",
            }
        ],
        "locations": [
            {
                "uuid": "l-1",
                "server_id": 7,
                "company_server_id": 1,
                "name": "Armazém",
                "is_active": 1,
                "synced": 1,
                "source": "server",
            }
        ],
    }

    apply_pull_payload(payload, conn_with_company)

    cat = conn_with_company.execute(
        "SELECT name FROM product_categories_local WHERE uuid = 'c-1'"
    ).fetchone()
    loc = conn_with_company.execute(
        "SELECT name FROM locations_local WHERE uuid = 'l-1'"
    ).fetchone()

    assert cat[0] == "Categoria"
    assert loc[0] == "Armazém"
