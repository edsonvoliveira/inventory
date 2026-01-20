# backend/tests/integration/sync/conftest.py

"""
Responsibilities:
- Integration fixtures for sync tests.
"""

import os
import pytest

from app.clients.supabase_client import get_supabase_service_client
from tests.helpers.test_user import FakeCurrentUser


@pytest.fixture(scope="session", autouse=True)
def require_env():
    required = [
        "TEST_COMPANY_ID",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
    ]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.skip(f"Missing env vars: {', '.join(missing)}")


@pytest.fixture(scope="session")
def supabase():
    return get_supabase_service_client()


@pytest.fixture(scope="session")
def company_id() -> int:
    return int(os.environ["TEST_COMPANY_ID"])


@pytest.fixture(scope="session")
def manager_user(company_id: int) -> FakeCurrentUser:
    db_user_id = int(os.environ.get("TEST_DB_USER_ID", "1"))
    return FakeCurrentUser(
        company_server_id=company_id,
        db_user_id=db_user_id,
        role="manager",
    )


@pytest.fixture(scope="session")
def counter_user(company_id: int) -> FakeCurrentUser:
    db_user_id = int(os.environ.get("TEST_DB_USER_ID", "1"))
    return FakeCurrentUser(
        company_server_id=company_id,
        db_user_id=db_user_id,
        role="counter",
    )


@pytest.fixture(scope="session")
def admin_user(company_id: int) -> FakeCurrentUser:
    db_user_id = int(os.environ.get("TEST_DB_USER_ID", "1"))
    return FakeCurrentUser(
        company_server_id=company_id,
        db_user_id=db_user_id,
        role="admin",
    )
