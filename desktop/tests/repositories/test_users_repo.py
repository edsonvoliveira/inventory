# desktop/tests/repositories/test_users_repo.py

"""
Responsibilities:
- Test users repo behavior.
"""

#desktop/tests/repositories/test_users_repo.py

"""
Responsabilities:
- Unit tests for UsersRepo
- Participate in bootstrap and sync pull operations
- Don't test in sync push operations
- Don't test CRUD operations from the UI
- Uses in-memory SQLite database for isolation
- Focused in pull, read-only and reset scenarios
"""

from desktop.data.repositories.users_repo import UsersRepo

def test_users_upsert_many(conn_with_company):
    repo = UsersRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "email": "user@test.com",
            "username": "user1",
            "name": "User One",
            "role": "admin",
            "company_server_id": 1,
            "is_active": 1,
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT email, role, is_active, source
        FROM users_local
        WHERE uuid = 'u-1'
        """
    ).fetchone()

    assert row == ("user@test.com", "admin", 1, "server")


def test_users_soft_delete_from_server(conn_with_company):
    repo = UsersRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "email": "user@test.com",
            "name": "User One",
            "role": "admin",
            "company_server_id": 1,
            "is_active": 1,
            "source": "server",
        }
    ])

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "email": "user@test.com",   # linha completa
            "name": "User One",
            "role": "admin",
            "company_server_id": 1,
            "is_active": 0,
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        }
    ])

    row = conn_with_company.execute(
        """
        SELECT deleted_at, is_active
        FROM users_local
        WHERE uuid = 'u-1'
        """
    ).fetchone()

    assert row[0] is not None
    assert row[1] == 0


def test_users_get_all_active_only(conn_with_company):
    repo = UsersRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "email": "a@test.com",
            "name": "Ativo",
            "role": "admin",
            "company_server_id": 1,
            "is_active": 1,
            "source": "server",
        },
        {
            "uuid": "u-2",
            "server_id": 11,
            "email": "i@test.com",
            "name": "Inativo",
            "role": "user",
            "company_server_id": 1,
            "is_active": 0,
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        },
    ])

    rows = repo.get_all()
    names = {r["name"] for r in rows}

    assert "Ativo" in names
    assert "Inativo" not in names


def test_users_get_all_including_deleted(conn_with_company):
    repo = UsersRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "email": "a@test.com",
            "name": "Ativo",
            "role": "admin",
            "company_server_id": 1,
            "is_active": 1,
            "source": "server",
        },
        {
            "uuid": "u-2",
            "server_id": 11,
            "email": "i@test.com",
            "name": "Inativo",
            "role": "user",
            "company_server_id": 1,
            "is_active": 0,
            "deleted_at": "2025-01-01T10:00:00Z",
            "source": "server",
        },
    ])

    rows = repo.get_all(active_only=False)
    names = {r["name"] for r in rows}

    assert "Ativo" in names
    assert "Inativo" in names


def test_users_get_by_uuid(conn_with_company):
    repo = UsersRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "email": "user@test.com",
            "name": "User",
            "role": "admin",
            "company_server_id": 1,
            "is_active": 1,
            "source": "server",
        }
    ])

    row = repo.get_by_uuid("u-1")

    assert row is not None
    assert row["email"] == "user@test.com"


def test_users_delete_all(conn_with_company):
    repo = UsersRepo(conn_with_company)

    repo.upsert_many([
        {
            "uuid": "u-1",
            "server_id": 10,
            "email": "user@test.com",
            "name": "User",
            "role": "admin",
            "company_server_id": 1,
            "source": "server",
        }
    ])

    repo.delete_all()

    count = conn_with_company.execute(
        "SELECT COUNT(*) FROM users_local"
    ).fetchone()[0]

    assert count == 0