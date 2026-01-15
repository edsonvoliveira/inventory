# backend/tests/conftest.py

"""
Responsibilities:
- Define pytest fixtures for this test scope.
- Configure test environment setup and teardown.
"""

#backend/tests/conftest.py

import os
import pytest
from tests.helpers.test_user import FakeCurrentUser


@pytest.fixture
def test_user() -> FakeCurrentUser:
    company_id = int(os.environ["TEST_COMPANY_ID"])
    db_user_id = int(os.environ.get("TEST_DB_USER_ID", "1"))

    return FakeCurrentUser(
        company_server_id=company_id,
        db_user_id=db_user_id,
    )
