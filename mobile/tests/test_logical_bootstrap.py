# mobile/tests/test_logical_bootstrap.py

"""
Responsibilities:
- Test logical bootstrap behavior.
"""

import os

import pytest

from mobile.bootstrap.bootstrap import bootstrap_app
from mobile.core.sync_service import ensure_bootstrap_for_company
from mobile.data.repositories.app_meta_repo import get_meta, set_meta
from mobile.config.settings import DB_PATH


def test_logical_bootstrap():
    print("=== TESTE BOOTSTRAP LOGICO MOBILE ===")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    bootstrap_app()

    jwt_token = os.environ.get("JWT_TOKEN", "").strip()
    if not jwt_token:
        pytest.skip("JWT_TOKEN nao definido para sync pull")
    set_meta("jwt_token", jwt_token)

    executed = ensure_bootstrap_for_company(
        company_id=1,
        company_uuid="company-uuid-1"
    )

    assert executed is True
    assert get_meta("company_id") == "1"
    assert get_meta("bootstrap_done") in {"1", "true"}

