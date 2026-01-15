# mobile/data/queries.py

"""
Responsibilities:
- Module responsibilities not classified.
"""

import json
import os
import sqlite3
import threading
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from mobile.data.db.schema import SCHEMA_SQL, SCHEMA_VERSION
from mobile.data.migrations import ensure_meta_table, get_schema_version, migrate_schema, set_schema_version

try:
    from config.settings import DB_PATH
except ImportError:
    from mobile.config.settings import DB_PATH

_lock = threading.Lock()


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    with _lock, get_conn() as conn:
        ensure_meta_table(conn)
        current_version = get_schema_version(conn)
        if current_version == 0:
            conn.executescript(SCHEMA_SQL)
            set_schema_version(conn, SCHEMA_VERSION)
        elif current_version < SCHEMA_VERSION:
            migrate_schema(conn, current_version, SCHEMA_VERSION)
        elif current_version > SCHEMA_VERSION:
            raise RuntimeError(
                f"DB schema version {current_version} is newer than app schema {SCHEMA_VERSION}"
            )
        conn.commit()


def reset_db() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()


# -------------------------------------------------------
# Local profile (stored in app_meta)
# -------------------------------------------------------

def save_local_profile(username: str, password: str):
    payload = {"username": username, "password": password, "role": "Operador"}
    with _lock, get_conn() as conn:
        conn.execute(
            "INSERT INTO app_meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("profile", json.dumps(payload)),
        )
        conn.commit()


def get_local_profile() -> Optional[Dict[str, Any]]:
    with _lock, get_conn() as conn:
        cur = conn.execute("SELECT value FROM app_meta WHERE key = ?", ("profile",))
        row = cur.fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return None


# -------------------------------------------------------
# Lookup queries
# -------------------------------------------------------

def list_locations() -> List[Dict[str, Any]]:
    with _lock, get_conn() as conn:
        cur = conn.execute(
            "SELECT server_id, name, code FROM locations_local ORDER BY name"
        )
        rows = cur.fetchall()
        return [{"id": r[0], "name": r[1], "code": r[2]} for r in rows]


def list_events_for_location(location_id: int) -> List[Dict[str, Any]]:
    with _lock, get_conn() as conn:
        cur = conn.execute(
            "SELECT server_id, location_server_id, title, status "
            "FROM inventory_events_local WHERE location_server_id = ? AND status = 'planned' ORDER BY server_id",
            (location_id,),
        )
        rows = cur.fetchall()
        return [{"id": r[0], "location_id": r[1], "title": r[2], "status": r[3]} for r in rows]


def list_zones_for_event(event_id: int) -> List[Dict[str, Any]]:
    with _lock, get_conn() as conn:
        cur = conn.execute(
            "SELECT server_id, event_server_id, name FROM zones_local WHERE event_server_id = ? ORDER BY server_id",
            (event_id,),
        )
        rows = cur.fetchall()
        return [{"id": r[0], "event_id": r[1], "name": r[2]} for r in rows]


def list_products() -> List[Dict[str, Any]]:
    with _lock, get_conn() as conn:
        cur = conn.execute(
            "SELECT server_id, sku, name, uom_inventory FROM products_local ORDER BY name"
        )
        rows = cur.fetchall()
        return [{"id": r[0], "sku": r[1], "name": r[2], "uom_inventory": r[3]} for r in rows]


# -------------------------------------------------------
# Inventory outbox
# -------------------------------------------------------

def _to_uuid(value: int) -> str:
    return f"server:{value}"


def add_local_inventory_item(
    zone_id: int,
    event_id: int,
    username: str,
    scanned_code: str,
    product_id: Optional[int],
    qty_counted: float,
    batch_number: Optional[str] = None,
    expiry_date: Optional[str] = None,
    is_new_product: int = 0,
    notes: Optional[str] = None,
):
    ts = datetime.utcnow().isoformat()
    record_uuid = str(uuid.uuid4())
    event_uuid = _to_uuid(event_id)
    zone_uuid = _to_uuid(zone_id)
    user_uuid = username or "local"
    user_server_id = 0
    product_uuid = _to_uuid(product_id) if product_id else None

    with _lock, get_conn() as conn:
        conn.execute(
            """
            INSERT INTO inventory_items_local
            (uuid, event_uuid, event_server_id, zone_uuid, zone_server_id,
             user_uuid, user_server_id, product_uuid, product_server_id,
             scanned_code, qty_counted, batch_number, expiry_date,
             is_new_product, device_timestamp, source, created_at, synced)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                record_uuid,
                event_uuid,
                event_id,
                zone_uuid,
                zone_id,
                user_uuid,
                user_server_id,
                product_uuid,
                product_id,
                scanned_code,
                qty_counted,
                batch_number,
                expiry_date,
                is_new_product,
                ts,
                "mobile",
                ts,
                0,
            ),
        )
        conn.commit()


def list_pending_inventory_items(event_id: int, zone_id: int) -> List[Dict[str, Any]]:
    with _lock, get_conn() as conn:
        cur = conn.execute(
            """
            SELECT product_server_id, qty_counted
            FROM inventory_items_local
            WHERE zone_server_id=? AND event_server_id=?
            """,
            (zone_id, event_id),
        )
        rows = cur.fetchall()
        return [{"product_id": r[0], "qty_counted": r[1]} for r in rows]


# -------------------------------------------------------
# Statistics
# -------------------------------------------------------

def list_counted_product_ids(event_id: int, zone_id: int) -> List[int]:
    with _lock, get_conn() as conn:
        cur = conn.execute(
            """
            SELECT DISTINCT product_server_id
            FROM inventory_items_local
            WHERE zone_server_id = ? AND event_server_id = ? AND product_server_id IS NOT NULL
            """,
            (zone_id, event_id),
        )
        rows = cur.fetchall()
        return [r[0] for r in rows]


def count_distinct_products_for_zone(event_id: int, zone_id: int) -> int:
    with _lock, get_conn() as conn:
        cur = conn.execute(
            """
            SELECT COUNT(DISTINCT product_server_id)
            FROM inventory_items_local
            WHERE zone_server_id = ? AND event_server_id = ? AND product_server_id IS NOT NULL
            """,
            (zone_id, event_id),
        )
        row = cur.fetchone()
        return row[0] if row else 0


# -------------------------------------------------------
# Seeds
# -------------------------------------------------------

def seed_minimal_data() -> None:
    from mobile.data.seeds.seed_minimal_test_data import seed_minimal_data
    with _lock, get_conn() as conn:
        seed_minimal_data(conn)
        conn.commit()
