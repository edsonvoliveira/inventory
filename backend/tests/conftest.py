# backend/tests/conftest.py

"""
Responsibilities:
- Define pytest fixtures for this test scope.
- Configure test environment setup and teardown.
"""

#backend/tests/conftest.py

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")
user_env = BACKEND_DIR / ".user_test"
if user_env.exists():
    load_dotenv(user_env, override=True)

from tests.helpers.test_user import FakeCurrentUser


@pytest.fixture
def test_user() -> FakeCurrentUser:
    company_id = int(os.environ["TEST_COMPANY_ID"])
    db_user_id = int(os.environ.get("TEST_DB_USER_ID", "1"))

    return FakeCurrentUser(
        company_server_id=company_id,
        db_user_id=db_user_id,
    )
