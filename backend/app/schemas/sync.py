# backend/app/schemas/sync.py

"""
Responsibilities:
- Pydantic schemas for sync data.
- Define request and response shapes.
"""

# app/schemas/sync.py

from typing import List, Dict, Any
from pydantic import BaseModel


# ======================================================
# SYNC PUSH
# ======================================================

class SyncItem(BaseModel):
    table_name: str
    operation: str
    record_uuid: str
    payload: Dict[str, Any]


class SyncPushRequest(BaseModel):
    items: List[SyncItem]


class SyncPushResponse(BaseModel):
    accepted: List[str]
    failed: List[str]


# ======================================================
# SYNC BOOTSTRAP
# ======================================================

class SyncBootstrapResponse(BaseModel):
    companies: List[Dict[str, Any]]
    users: List[Dict[str, Any]]
    locations: List[Dict[str, Any]]
    product_categories: List[Dict[str, Any]]
    products: List[Dict[str, Any]]
    product_barcodes: List[Dict[str, Any]]
    inventory_events: List[Dict[str, Any]]
    inventory_event_targets: List[Dict[str, Any]]
    zones: List[Dict[str, Any]]
    server_ts: str
