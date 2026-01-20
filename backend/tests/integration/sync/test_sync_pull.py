# backend/tests/integration/sync/test_sync_pull.py

"""
Responsibilities:
- Validate pull behavior (bootstrap/incremental) for sync.
"""

from datetime import datetime, timedelta, timezone

from app.services.sync.pull_executor import PullExecutor
from tests.helpers.sync_data import create_product, cleanup_by_uuid


def test_pull_incremental_returns_updated_rows(supabase, company_id):
    record = create_product(supabase, company_id)
    record_uuid = record["uuid"]

    since = datetime.now(timezone.utc) - timedelta(days=1)

    try:
        payload = PullExecutor().execute(
            company_server_id=company_id,
            since=since,
        )
        assert "server_ts" in payload
        products = payload.get("products", [])
        assert any(row.get("uuid") == record_uuid for row in products)
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)
