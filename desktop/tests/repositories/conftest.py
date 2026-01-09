#desktop/tests/repositories/conftest.py
"""
Responsabilities:
- Pytest configuration for repository tests
- Shared fixtures and setup/teardown logic
"""

import pytest
import sqlite3
from desktop.tests.helpers.db import make_test_connection
from desktop.data.repositories.app_meta_repo import set_meta

@pytest.fixture
def conn_with_company() -> sqlite3.Connection:
    conn = make_test_connection()
    set_meta("company_server_id", "1", conn)
    return conn

