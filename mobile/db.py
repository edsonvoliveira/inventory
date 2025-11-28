# db.py
import sqlite3
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = "mobile_local.db"
_lock = threading.Lock()

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with _lock, get_conn() as conn:
        c = conn.cursor()
        # 1. local_user_profile (ajustada para username e password)
        c.execute("""
        CREATE TABLE IF NOT EXISTS local_user_profile (
            username TEXT PRIMARY KEY NOT NULL,
            password TEXT NOT NULL
        );
        """)
        # 2. lookup tables (mantidas iguais)
        c.execute("""
        CREATE TABLE IF NOT EXISTS local_locations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS local_events (
            id INTEGER PRIMARY KEY,
            location_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS local_zones (
            id INTEGER PRIMARY KEY,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS local_products (
            id INTEGER PRIMARY KEY,
            sku TEXT NOT NULL,
            name TEXT NOT NULL,
            uom_inventory TEXT
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS local_barcodes (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            barcode TEXT NOT NULL UNIQUE
        );
        """)
        # 3. outbox table (ajustada para username)
        c.execute("""
        CREATE TABLE IF NOT EXISTS local_inventory_items (
            local_id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            scanned_code TEXT NOT NULL,
            product_id INTEGER,
            qty_counted REAL NOT NULL,
            batch_number TEXT,
            expiry_date TEXT,
            is_new_product INTEGER NOT NULL,
            notes TEXT,
            device_timestamp TEXT NOT NULL,
            sync_status TEXT NOT NULL DEFAULT 'PENDING'
        );
        """)
        conn.commit()

# User profile helpers (ajustadas para username e password)
def save_local_profile(username: str, password: str):
    with _lock, get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO local_user_profile (username, password)
            VALUES (?, ?)
        """, (username, password))
        conn.commit()

def get_local_profile() -> Optional[Dict[str,Any]]:
    with _lock, get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT username, password FROM local_user_profile LIMIT 1")
        row = c.fetchone()
        if not row:
            return None
        keys = ["username", "password"]
        return dict(zip(keys, row))

# Lookup queries (mantidas iguais)
def list_locations() -> List[Dict[str,Any]]:
    with _lock, get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id,name,code FROM local_locations ORDER BY name")
        rows = c.fetchall()
        return [{"id":r[0],"name":r[1],"code":r[2]} for r in rows]

def list_events_for_location(location_id:int) -> List[Dict[str,Any]]:
    with _lock, get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id,location_id,title,status FROM local_events WHERE location_id=? AND status IN ('open','counting') ORDER BY id", (location_id,))
        rows = c.fetchall()
        return [{"id":r[0],"location_id":r[1],"title":r[2],"status":r[3]} for r in rows]

def list_zones_for_event(event_id:int) -> List[Dict[str,Any]]:
    with _lock, get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id,event_id,name FROM local_zones WHERE event_id=? ORDER BY id", (event_id,))
        rows = c.fetchall()
        return [{"id":r[0],"event_id":r[1],"name":r[2]} for r in rows]

def find_product_by_barcode(barcode:str) -> Optional[Dict[str,Any]]:
    with _lock, get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT p.id, p.sku, p.name, p.uom_inventory
            FROM local_barcodes b
            JOIN local_products p ON p.id = b.product_id
            WHERE b.barcode = ? LIMIT 1
        """, (barcode,))
        r = c.fetchone()
        if not r:
            return None
        return {"id": r[0], "sku": r[1], "name": r[2], "uom_inventory": r[3]}

# Outbox functions (ajustada para username)
def add_local_inventory_item(zone_id:int, username:str, scanned_code:str,
                             product_id:Optional[int], qty_counted:float,
                             batch_number:Optional[str], expiry_date:Optional[str],
                             is_new_product:int, notes:Optional[str]):
    ts = datetime.utcnow().isoformat()
    with _lock, get_conn() as conn:
        conn.execute("""
            INSERT INTO local_inventory_items
            (zone_id, username, scanned_code, product_id, qty_counted, batch_number, expiry_date, is_new_product, notes, device_timestamp, sync_status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (zone_id, username, scanned_code, product_id, qty_counted, batch_number, expiry_date, is_new_product, notes, ts, 'PENDING'))
        conn.commit()

def list_pending_inventory_items() -> List[Dict[str,Any]]:
    with _lock, get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT local_id, zone_id, username, scanned_code, product_id, qty_counted, batch_number, expiry_date, is_new_product, notes, device_timestamp, sync_status
            FROM local_inventory_items
            ORDER BY local_id DESC
            LIMIT 500
        """)
        rows = c.fetchall()
        keys = ["local_id","zone_id","username","scanned_code","product_id","qty_counted","batch_number","expiry_date","is_new_product","notes","device_timestamp","sync_status"]
        return [dict(zip(keys,r)) for r in rows]

def mark_item_status(local_id:int, status:str):
    with _lock, get_conn() as conn:
        conn.execute("UPDATE local_inventory_items SET sync_status=? WHERE local_id=?", (status, local_id))
        conn.commit()
