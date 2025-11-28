import sqlite3
from typing import List, Dict, Any, Optional

DB_PATH = "inventory.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

# -------------------- COMPANY CRUD --------------------
def company_create(name: str, nif: Optional[str] = None):
    with get_conn() as conn:
        conn.execute("INSERT INTO Company (name, nif) VALUES (?, ?)", (name, nif))
        conn.commit()

def company_get_all() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Company")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]

def company_get(id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Company WHERE id=?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None

def company_update(id: int, name: str, nif: Optional[str]):
    with get_conn() as conn:
        conn.execute("UPDATE Company SET name=?, nif=? WHERE id=?", (name, nif, id))
        conn.commit()

def company_delete(id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM Company WHERE id=?", (id,))
        conn.commit()

# -------------------- ROLE CRUD --------------------
def role_create(name: str):
    with get_conn() as conn:
        conn.execute("INSERT INTO Role (name) VALUES (?)", (name,))
        conn.commit()

def role_get_all():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Role")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]

def role_get(id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Role WHERE id=?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None

def role_update(id: int, name: str):
    with get_conn() as conn:
        conn.execute("UPDATE Role SET name=? WHERE id=?", (name, id))
        conn.commit()

def role_delete(id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM Role WHERE id=?", (id,))
        conn.commit()

# -------------------- USER CRUD --------------------
def user_create(email: str, password_hash: str, role_id: int, company_id: int, is_active: int = 1):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO User (email, password_hash, role_id, company_id, is_active) VALUES (?, ?, ?, ?, ?)",
            (email, password_hash, role_id, company_id, is_active)
        )
        conn.commit()

def user_get_all():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM User")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]

def user_get(id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM User WHERE id=?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None

def user_update(id: int, email: str, password_hash: str, role_id: int, company_id: int, is_active: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE User SET email=?, password_hash=?, role_id=?, company_id=?, is_active=? WHERE id=?",
            (email, password_hash, role_id, company_id, is_active, id)
        )
        conn.commit()

def user_delete(id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM User WHERE id=?", (id,))
        conn.commit()

# -------------------- LOCATION CRUD --------------------
def location_create(name: str, company_id: int):
    with get_conn() as conn:
        conn.execute("INSERT INTO Location (name, company_id) VALUES (?, ?)", (name, company_id))
        conn.commit()

def location_get_all():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Location")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]

def location_get(id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Location WHERE id=?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None

def location_update(id: int, name: str, company_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE Location SET name=?, company_id=? WHERE id=?", (name, company_id, id))
        conn.commit()

def location_delete(id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM Location WHERE id=?", (id,))
        conn.commit()

# -------------------- PRODUCT CRUD --------------------
def product_create(sku: str, barcode: str, name: str, unit_cost: float, unit_of_measure: str, last_updated: str, company_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO Product (sku, barcode, name, unit_cost, unit_of_measure, last_updated, company_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sku, barcode, name, unit_cost, unit_of_measure, last_updated, company_id)
        )
        conn.commit()

def product_get_all():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Product")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]

def product_get(id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Product WHERE id=?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None

def product_update(id: int, sku: str, barcode: str, name: str, unit_cost: float, unit_of_measure: str, last_updated: str, company_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE Product SET sku=?, barcode=?, name=?, unit_cost=?, unit_of_measure=?, last_updated=?, company_id=? WHERE id=?",
            (sku, barcode, name, unit_cost, unit_of_measure, last_updated, company_id, id)
        )
        conn.commit()

def product_delete(id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM Product WHERE id=?", (id,))
        conn.commit()

# -------------------- STOCK LOCATION CRUD --------------------
def stock_location_create(product_id: int, location_id: int, current_stock: float, reorder_point: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO Stock_Location (product_id, location_id, current_stock, reorder_point) VALUES (?, ?, ?, ?)",
            (product_id, location_id, current_stock, reorder_point)
        )
        conn.commit()

def stock_location_get_all():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Stock_Location")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]

def stock_location_get(id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Stock_Location WHERE id=?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None

def stock_location_update(id: int, product_id: int, location_id: int, current_stock: float, reorder_point: float):
    with get_conn() as conn:
        conn.execute(
            "UPDATE Stock_Location SET product_id=?, location_id=?, current_stock=?, reorder_point=? WHERE id=?",
            (product_id, location_id, current_stock, reorder_point, id)
        )
        conn.commit()

def stock_location_delete(id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM Stock_Location WHERE id=?", (id,))
        conn.commit()

# -------------------- MOVEMENT CRUD --------------------
def movement_create(product_id: int, location_id: int, type_: str, quantity: float, date_time: str, reference: Optional[str], user_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO Movement (product_id, location_id, type, quantity, date_time, reference, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (product_id, location_id, type_, quantity, date_time, reference, user_id)
        )
        conn.commit()

def movement_get_all():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Movement")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]

def movement_get(id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM Movement WHERE id=?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None

def movement_update(id: int, product_id: int, location_id: int, type_: str, quantity: float, date_time: str, reference: Optional[str], user_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE Movement SET product_id=?, location_id=?, type=?, quantity=?, date_time=?, reference=?, user_id=? WHERE id=?",
            (product_id, location_id, type_, quantity, date_time, reference, user_id, id)
        )
        conn.commit()

def movement_delete(id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM Movement WHERE id=?", (id,))
        conn.commit()
