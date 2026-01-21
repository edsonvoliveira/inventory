# desktop/data/repositories/sync_allowlist.py

"""
Responsibilities:
- Define allowed sync fields per entity/operation.
"""

from __future__ import annotations

from typing import Iterable


_ALLOWLISTS: dict[str, dict[str, set[str]]] = {
    "product_categories": {
        "insert": {"code", "name", "description", "is_active"},
        "update": {"code", "name", "description", "is_active"},
        "delete": {"is_active"},
    },
    "products": {
        "insert": {
            "sku",
            "name",
            "description",
            "category_id",
            "category_server_id",
            "category_uuid",
            "uom_base",
            "uom_inventory",
            "conversion_factor",
            "cost_price",
            "is_sensitive",
            "serial_number_enabled",
            "is_active",
        },
        "update": {
            "name",
            "description",
            "category_id",
            "category_server_id",
            "category_uuid",
            "uom_base",
            "uom_inventory",
            "conversion_factor",
            "cost_price",
            "is_sensitive",
            "serial_number_enabled",
            "is_active",
        },
        "delete": {"is_active"},
    },
    "product_barcodes": {
        "insert": {"product_id", "product_server_id", "product_uuid", "barcode", "description", "is_active"},
        "update": {"barcode", "description", "is_active"},
        "delete": {"is_active"},
    },
    "locations": {
        "insert": {"code", "name", "address", "is_active"},
        "update": {"code", "name", "address", "is_active"},
        "delete": {"is_active"},
    },
    "inventory_events": {
        "insert": {
            "location_id",
            "location_server_id",
            "location_uuid",
            "title",
            "event_type",
            "status",
            "required_counts",
            "required_audits",
            "tolerance_percent",
            "tolerance_absolute",
            "is_active",
        },
        "update": {
            "title",
            "event_type",
            "status",
            "required_counts",
            "required_audits",
            "tolerance_percent",
            "tolerance_absolute",
        },
        "delete": {"is_active"},
    },
    "inventory_event_targets": {
        "insert": {
            "event_id",
            "event_server_id",
            "event_uuid",
            "product_id",
            "product_server_id",
            "product_uuid",
            "expected_qty",
            "is_active",
        },
        "update": {"expected_qty", "is_active"},
        "delete": {"is_active"},
    },
    "zones": {
        "insert": {
            "event_id",
            "event_server_id",
            "event_uuid",
            "name",
            "description",
            "count_status",
            "lock_status",
            "is_active",
        },
        "update": {"name", "description", "count_status", "lock_status", "is_active"},
        "delete": {"is_active"},
    },
    "inventory_items": {
        "insert": {
            "zone_id",
            "zone_server_id",
            "zone_uuid",
            "product_id",
            "product_server_id",
            "product_uuid",
            "qty_counted",
            "device_timestamp",
            "source",
            "user_id",
            "user_server_id",
            "user_uuid",
        },
        "update": {
            "qty_counted",
            "batch_number",
            "expiry_date",
            "scanned_code",
            "device_timestamp",
            "latitude",
            "longitude",
            "source",
            "user_id",
            "user_server_id",
        },
        "delete": set(),
    },
    "zone_user_progress": {
        "insert": {
            "zone_id",
            "zone_server_id",
            "zone_uuid",
            "user_id",
            "user_server_id",
            "user_uuid",
            "count_type",
            "started_at",
            "device_id",
            "items_counted",
            "qty_total",
            "is_finished",
            "finished_at",
        },
        "update": {"items_counted", "qty_total", "is_finished", "finished_at"},
        "delete": set(),
    },
}


def filter_payload(entity: str, operation: str, payload: dict) -> dict:
    allowed = _ALLOWLISTS.get(entity, {}).get(operation)
    if not allowed:
        return dict(payload)
    return {k: v for k, v in payload.items() if k in allowed}


def get_allowed_fields(entity: str, operation: str) -> Iterable[str]:
    return _ALLOWLISTS.get(entity, {}).get(operation, set())
