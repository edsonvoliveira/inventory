# backend/tests/integration/sync/test_sync_misc.py

"""
Responsibilities:
- Misc sync validations not covered elsewhere.
"""

from datetime import datetime, timezone

import pytest

from app.services.sync.handlers.companies import CompanySyncHandler
from app.services.sync.pull_executor import PullExecutor
from tests.helpers.sync_data import create_product, cleanup_by_uuid


def test_companies_push_rejected(manager_user):
    handler = CompanySyncHandler()
    with pytest.raises(RuntimeError) as excinfo:
        handler.insert(payload={}, record_uuid="dummy", user=manager_user)
    message = str(excinfo.value)
    assert "Companies" in message
    assert "suportam push via sync" in message


def test_deleted_at_not_in_pull_payload(supabase, company_id):
    record = create_product(supabase, company_id)
    record_uuid = record["uuid"]

    try:
        supabase.table("products").update(
            {"deleted_at": datetime.now(timezone.utc).isoformat()}
        ).eq("uuid", record_uuid).execute()

        payload = PullExecutor().execute(
            company_server_id=company_id,
            since=None,
        )
        products = payload.get("products", [])
        row = next(p for p in products if p.get("uuid") == record_uuid)
        assert "deleted_at" not in row
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)
