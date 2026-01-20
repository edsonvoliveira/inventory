# backend/tests/integration/schema/test_schema_contract.py

"""
Responsibilities:
- Validate schema constraints and timestamp types aligned to the sync contract.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from tests.helpers.sync_data import create_location, cleanup_by_uuid, create_product


def test_required_counts_check_constraint(supabase, company_id):
    location = create_location(supabase, company_id)
    record_uuid = str(uuid4())

    try:
        with pytest.raises(Exception):
            supabase.table("inventory_events").insert(
                {
                    "uuid": record_uuid,
                    "company_id": company_id,
                    "location_id": location["id"],
                    "title": "Evento Invalid",
                    "event_type": "count",
                    "status": "open",
                    "required_counts": 0,
                }
            ).execute()
    finally:
        cleanup_by_uuid(supabase, "locations", location["uuid"])


def test_unique_uuid_enforced_on_products(supabase, company_id):
    product = create_product(supabase, company_id)
    record_uuid = product["uuid"]

    try:
        with pytest.raises(Exception):
            supabase.table("products").insert(
                {
                    "uuid": record_uuid,
                    "company_id": company_id,
                    "sku": f"SKU-DUP-{record_uuid[:8]}",
                    "name": "Produto Duplicado",
                    "uom_base": "UN",
                    "uom_inventory": "UN",
                    "is_active": True,
                }
            ).execute()
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)


def test_timestamps_have_timezone(supabase, company_id):
    record_uuid = str(uuid4())
    supabase.table("products").insert(
        {
            "uuid": record_uuid,
            "company_id": company_id,
            "sku": f"SKU-TZ-{record_uuid[:8]}",
            "name": "Produto TZ",
            "uom_base": "UN",
            "uom_inventory": "UN",
            "is_active": True,
        }
    ).execute()

    try:
        resp = (
            supabase.table("products")
            .select("created_at, updated_at")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )
        row = resp.data[0]
        created_at = row.get("created_at")
        updated_at = row.get("updated_at")
        assert isinstance(created_at, str) and isinstance(updated_at, str)
        assert created_at.endswith("Z") or "+" in created_at
        assert updated_at.endswith("Z") or "+" in updated_at
    finally:
        cleanup_by_uuid(supabase, "products", record_uuid)
