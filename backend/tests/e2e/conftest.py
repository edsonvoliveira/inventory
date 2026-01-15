#tests/e2e/conftest.py (DO BACKEND, não do desktop)

import pytest
from app.main import app
from app.core.security import get_current_user
from tests.helpers.test_user import FakeCurrentUser

@pytest.fixture(scope="session", autouse=True)
def override_auth_dependency():
    test_user = FakeCurrentUser(
        company_server_id=1,
        db_user_id=1,
        email="e2e@test.local",
        is_admin=True,
    )

    app.dependency_overrides[get_current_user] = lambda: test_user
    yield
    app.dependency_overrides.clear()
