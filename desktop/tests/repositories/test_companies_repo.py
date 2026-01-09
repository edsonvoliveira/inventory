#desktop/tests/repositories/test_companies_repo.py

"""
Responsabilities:
- Unit tests for CompaniesRepo
- Not tested CUD operations, outbox functionality, and syncing behavior
- Uses an in-memory SQLite database for isolation
- Verifies correct handling of companies data
- Note: companies do not allow offline creation via UI
"""

from desktop.data.repositories.companies_repo import CompaniesRepo


def test_companies_upsert_many(conn_with_company):
    repo = CompaniesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "c-1",
            "server_id": 1,
            "name": "Empresa Teste",
            "country_code": "PT",
            "is_active": 1,
            "synced": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT name, country_code, synced, source
        FROM companies_local
        WHERE uuid = 'c-1'
        """
    ).fetchone()

    assert row == ("Empresa Teste", "PT", 1, "server")


def test_companies_soft_delete_from_server(conn_with_company):
    repo = CompaniesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "c-1",
            "server_id": 1,
            "name": "Empresa",
            "is_active": 1,
            "source": "server",
        }
    ])

    repo.upsert_many([
        {
            "uuid": "c-1",
            "server_id": 1,
            "name": "Empresa",
            "deleted_at": "2025-01-01T10:00:00Z",
            "is_active": 0,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active
        FROM companies_local
        WHERE uuid = 'c-1'
        """
    ).fetchone()

    assert row[0] is not None
    assert row[1] == 0


def test_companies_get_all_active_only(conn_with_company):
    repo = CompaniesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "c-1",
            "server_id": 1,
            "name": "Ativa",
            "is_active": 1,
            "source": "server",
        },
        {
            "uuid": "c-2",
            "server_id": 2,
            "name": "Inativa",
            "is_active": 0,
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        },
    ])

    rows = repo.get_all()
    names = {r["name"] for r in rows}

    assert "Ativa" in names
    assert "Inativa" not in names


def test_companies_get_all_including_deleted(conn_with_company):
    repo = CompaniesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "c-1",
            "server_id": 1,
            "name": "Ativa",
            "is_active": 1,
            "source": "server",
        },
        {
            "uuid": "c-2",
            "server_id": 2,
            "name": "Inativa",
            "is_active": 0,
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        },
    ])

    rows = repo.get_all(active_only=False)
    names = {r["name"] for r in rows}

    assert "Ativa" in names
    assert "Inativa" in names


def test_companies_get_by_uuid(conn_with_company):
    repo = CompaniesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "c-1",
            "server_id": 1,
            "name": "Empresa",
            "country_code": "PT",
            "source": "server",
        }
    ])

    row = repo.get_by_uuid("c-1")

    assert row is not None
    assert row["name"] == "Empresa"


def test_companies_delete_all(conn_with_company):
    repo = CompaniesRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "c-1",
            "server_id": 1,
            "name": "Empresa",
            "source": "server",
        }
    ])

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM companies_local"
    ).fetchone()[0]

    assert count == 0
