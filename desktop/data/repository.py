# desktop/data/repository.py

"""
Responsibilities:
- Module responsibilities not classified.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import get_meta, set_meta

DEFAULT_ROLES = ("admin", "manager", "coordinator", "auditor", "counter")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_conn():
    return get_connection()


def _next_local_server_id(conn, key: str) -> int:
    current = get_meta(key, conn)
    if current is None:
        value = -1
    else:
        value = int(current)
    set_meta(key, str(value - 1), conn)
    return value


def _ensure_roles_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS roles_local (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE
        )
        """
    )
    row = conn.execute("SELECT COUNT(1) FROM roles_local").fetchone()
    if row and row[0] == 0:
        conn.executemany(
            "INSERT INTO roles_local (name) VALUES (?)",
            [(role,) for role in DEFAULT_ROLES],
        )
    conn.commit()


def _role_name_by_id(conn, role_id: int) -> Optional[str]:
    row = conn.execute("SELECT name FROM roles_local WHERE id = ?", (role_id,)).fetchone()
    return row[0] if row else None


def _role_id_by_name(conn, role_name: str) -> Optional[int]:
    row = conn.execute("SELECT id FROM roles_local WHERE name = ?", (role_name,)).fetchone()
    return row[0] if row else None


def _company_by_id(conn, company_id: int):
    return conn.execute(
        """
        SELECT id, server_id, name, vat_number
        FROM companies_local
        WHERE id = ? AND deleted_at IS NULL
        """,
        (company_id,),
    ).fetchone()


def _company_id_by_server_id(conn, company_server_id: int) -> Optional[int]:
    row = conn.execute(
        "SELECT id FROM companies_local WHERE server_id = ? AND deleted_at IS NULL",
        (company_server_id,),
    ).fetchone()
    return row[0] if row else None


# -------------------- COMPANY CRUD --------------------
def company_create(name: str, nif: Optional[str] = None):
    with _get_conn() as conn:
        now = _now()
        uuid = str(uuid4())
        server_id = _next_local_server_id(conn, "local_server_id_seq_companies")
        conn.execute(
            """
            INSERT INTO companies_local (
              uuid, server_id, name, vat_number, is_active,
              created_at, updated_at, deleted_at, synced, synced_at, source
            )
            VALUES (?, ?, ?, ?, 1, ?, ?, NULL, 0, NULL, 'desktop')
            """,
            (uuid, server_id, name, nif, now, now),
        )
        conn.commit()


def company_get_all() -> List[Dict[str, Any]]:
    with _get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, name, vat_number AS nif
            FROM companies_local
            WHERE deleted_at IS NULL
            ORDER BY id
            """
        )
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]


def company_get(id: int):
    with _get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, name, vat_number AS nif
            FROM companies_local
            WHERE id = ? AND deleted_at IS NULL
            """,
            (id,),
        )
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None


def company_get_local_id_by_server_id(company_server_id: int) -> Optional[int]:
    with _get_conn() as conn:
        return _company_id_by_server_id(conn, company_server_id)


def company_update(id: int, name: str, nif: Optional[str]):
    with _get_conn() as conn:
        now = _now()
        conn.execute(
            """
            UPDATE companies_local
            SET name = ?, vat_number = ?, updated_at = ?, synced = 0, synced_at = NULL, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (name, nif, now, id),
        )
        conn.commit()


def company_delete(id: int):
    with _get_conn() as conn:
        now = _now()
        conn.execute(
            """
            UPDATE companies_local
            SET deleted_at = ?, is_active = 0, updated_at = ?, synced = 0, synced_at = NULL, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (now, now, id),
        )
        conn.commit()


# -------------------- ROLE CRUD --------------------
def role_create(name: str):
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        conn.execute("INSERT INTO roles_local (name) VALUES (?)", (name,))
        conn.commit()


def role_get_all():
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        cur = conn.execute("SELECT id, name FROM roles_local ORDER BY id")
        rows = cur.fetchall()
    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]


def role_get(id: int):
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        cur = conn.execute("SELECT id, name FROM roles_local WHERE id = ?", (id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None


def role_update(id: int, name: str):
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        old = conn.execute("SELECT name FROM roles_local WHERE id = ?", (id,)).fetchone()
        if not old:
            return
        old_name = old[0]
        conn.execute("UPDATE roles_local SET name = ? WHERE id = ?", (name, id))
        conn.execute("UPDATE users_local SET role = ? WHERE role = ?", (name, old_name))
        conn.commit()


def role_delete(id: int):
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        row = conn.execute("SELECT name FROM roles_local WHERE id = ?", (id,)).fetchone()
        if not row:
            return
        role_name = row[0]
        in_use = conn.execute(
            "SELECT COUNT(1) FROM users_local WHERE role = ? AND deleted_at IS NULL",
            (role_name,),
        ).fetchone()
        if in_use and in_use[0] > 0:
            raise RuntimeError("Nao e possivel remover uma role em uso")
        conn.execute("DELETE FROM roles_local WHERE id = ?", (id,))
        conn.commit()


# -------------------- USER CRUD --------------------
def user_create(email: str, role_id: int, company_id: int, is_active: int = 1):
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        role_name = _role_name_by_id(conn, role_id)
        if not role_name:
            raise ValueError("role_id invalido")
        company = _company_by_id(conn, company_id)
        if not company:
            raise ValueError("company_id invalido")
        company_server_id = company[1]
        now = _now()
        uuid = str(uuid4())
        server_id = _next_local_server_id(conn, "local_server_id_seq_users")
        conn.execute(
            """
            INSERT INTO users_local (
              uuid, server_id, email, username, name, role, company_server_id, is_active,
              created_at, updated_at, deleted_at, last_sync_at, source
            )
            VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, NULL, NULL, 'desktop')
            """,
            (uuid, server_id, email, email, role_name, company_server_id, is_active, now, now),
        )
        conn.commit()


def user_get_all():
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        role_rows = conn.execute("SELECT id, name FROM roles_local").fetchall()
        role_name_to_id = {r[1]: r[0] for r in role_rows}
        company_rows = conn.execute(
            "SELECT id, server_id FROM companies_local WHERE deleted_at IS NULL"
        ).fetchall()
        company_server_to_id = {c[1]: c[0] for c in company_rows}
        cur = conn.execute(
            """
            SELECT id, email, role, company_server_id, is_active
            FROM users_local
            WHERE deleted_at IS NULL
            ORDER BY id
            """
        )
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]

    results = []
    for row in rows:
        data = dict(zip(cols, row))
        data["role_id"] = role_name_to_id.get(data.pop("role"))
        data["company_id"] = company_server_to_id.get(data.pop("company_server_id"))
        results.append(data)
    return results


def user_get(id: int):
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        cur = conn.execute(
            """
            SELECT id, email, role, company_server_id, is_active
            FROM users_local
            WHERE id = ? AND deleted_at IS NULL
            """,
            (id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        cols = [c[0] for c in cur.description]
        data = dict(zip(cols, row))
        data["role_id"] = _role_id_by_name(conn, data.pop("role"))
        data["company_id"] = _company_id_by_server_id(conn, data.pop("company_server_id"))
        return data


def user_update(id: int, email: str, role_id: int, company_id: int, is_active: int):
    with _get_conn() as conn:
        _ensure_roles_table(conn)
        role_name = _role_name_by_id(conn, role_id)
        if not role_name:
            raise ValueError("role_id invalido")
        company = _company_by_id(conn, company_id)
        if not company:
            raise ValueError("company_id invalido")
        company_server_id = company[1]
        now = _now()
        conn.execute(
            """
            UPDATE users_local
            SET email = ?, role = ?, company_server_id = ?, is_active = ?,
                updated_at = ?, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (email, role_name, company_server_id, is_active, now, id),
        )
        conn.commit()


def user_delete(id: int):
    with _get_conn() as conn:
        now = _now()
        conn.execute(
            """
            UPDATE users_local
            SET deleted_at = ?, is_active = 0, updated_at = ?, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (now, now, id),
        )
        conn.commit()


# -------------------- LOCATION CRUD --------------------
def location_create(name: str, company_id: int):
    with _get_conn() as conn:
        company = _company_by_id(conn, company_id)
        if not company:
            raise ValueError("company_id invalido")
        company_server_id = company[1]
        now = _now()
        uuid = str(uuid4())
        server_id = _next_local_server_id(conn, "local_server_id_seq_locations")
        conn.execute(
            """
            INSERT INTO locations_local (
              uuid, server_id, company_server_id, code, name, address, is_active,
              created_at, updated_at, deleted_at, synced, synced_at, source
            )
            VALUES (?, ?, ?, ?, ?, NULL, 1, ?, ?, NULL, 0, NULL, 'desktop')
            """,
            (uuid, server_id, company_server_id, name, name, now, now),
        )
        conn.commit()


def location_get_all():
    with _get_conn() as conn:
        company_rows = conn.execute(
            "SELECT id, server_id FROM companies_local WHERE deleted_at IS NULL"
        ).fetchall()
        company_server_to_id = {c[1]: c[0] for c in company_rows}
        cur = conn.execute(
            """
            SELECT id, name, company_server_id
            FROM locations_local
            WHERE deleted_at IS NULL
            ORDER BY id
            """
        )
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]

    results = []
    for row in rows:
        data = dict(zip(cols, row))
        data["company_id"] = company_server_to_id.get(data.pop("company_server_id"))
        results.append(data)
    return results


def location_get(id: int):
    with _get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, name, company_server_id
            FROM locations_local
            WHERE id = ? AND deleted_at IS NULL
            """,
            (id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        cols = [c[0] for c in cur.description]
        data = dict(zip(cols, row))
        data["company_id"] = _company_id_by_server_id(conn, data.pop("company_server_id"))
        return data


def location_update(id: int, name: str, company_id: int):
    with _get_conn() as conn:
        company = _company_by_id(conn, company_id)
        if not company:
            raise ValueError("company_id invalido")
        company_server_id = company[1]
        now = _now()
        conn.execute(
            """
            UPDATE locations_local
            SET name = ?, code = ?, company_server_id = ?, updated_at = ?, synced = 0,
                synced_at = NULL, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (name, name, company_server_id, now, id),
        )
        conn.commit()


def location_delete(id: int):
    with _get_conn() as conn:
        now = _now()
        conn.execute(
            """
            UPDATE locations_local
            SET deleted_at = ?, is_active = 0, updated_at = ?, synced = 0,
                synced_at = NULL, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (now, now, id),
        )
        conn.commit()


# -------------------- PRODUCT CRUD --------------------
def product_create(
    sku: str,
    barcode: str,
    name: str,
    unit_cost: float,
    unit_of_measure: str,
    last_updated: str,
    company_id: int,
):
    with _get_conn() as conn:
        company = _company_by_id(conn, company_id)
        if not company:
            raise ValueError("company_id invalido")
        company_server_id = company[1]
        now = last_updated or _now()
        uuid = str(uuid4())
        server_id = _next_local_server_id(conn, "local_server_id_seq_products")
        conn.execute(
            """
            INSERT INTO products_local (
              uuid, server_id, company_server_id, category_server_id, sku, name, description,
              uom_base, uom_inventory, conversion_factor, system_qty, cost_price,
              is_sensitive, serial_number_enabled, is_active,
              created_at, updated_at, deleted_at, synced, synced_at, source
            )
            VALUES (?, ?, ?, NULL, ?, ?, NULL, ?, ?, 1, 0, ?, 0, 0, 1, ?, ?, NULL, 0, NULL, 'desktop')
            """,
            (uuid, server_id, company_server_id, sku, name, unit_of_measure, unit_of_measure, unit_cost, now, now),
        )

        if barcode:
            barcode_uuid = str(uuid4())
            barcode_server_id = _next_local_server_id(conn, "local_server_id_seq_barcodes")
            conn.execute(
                """
                INSERT INTO product_barcodes_local (
                  uuid, server_id, company_server_id, product_server_id, barcode,
                  description, is_active, created_at, updated_at, deleted_at,
                  synced, synced_at, source
                )
                VALUES (?, ?, ?, ?, ?, NULL, 1, ?, ?, NULL, 0, NULL, 'desktop')
                """,
                (barcode_uuid, barcode_server_id, company_server_id, server_id, barcode, now, now),
            )
        conn.commit()


def product_get_all():
    with _get_conn() as conn:
        company_rows = conn.execute(
            "SELECT id, server_id FROM companies_local WHERE deleted_at IS NULL"
        ).fetchall()
        company_server_to_id = {c[1]: c[0] for c in company_rows}
        barcode_rows = conn.execute(
            """
            SELECT product_server_id, barcode
            FROM product_barcodes_local
            WHERE deleted_at IS NULL
            """
        ).fetchall()
        barcode_by_product = {b[0]: b[1] for b in barcode_rows}
        cur = conn.execute(
            """
            SELECT id, server_id, sku, name, cost_price, uom_inventory, updated_at, company_server_id
            FROM products_local
            WHERE deleted_at IS NULL
            ORDER BY id
            """
        )
        rows = cur.fetchall()

    results = []
    for row in rows:
        (
            product_id,
            product_server_id,
            sku,
            name,
            cost_price,
            uom_inventory,
            updated_at,
            company_server_id,
        ) = row
        results.append(
            {
                "id": product_id,
                "sku": sku,
                "barcode": barcode_by_product.get(product_server_id, ""),
                "name": name,
                "unit_cost": cost_price,
                "unit_of_measure": uom_inventory,
                "last_updated": updated_at,
                "company_id": company_server_to_id.get(company_server_id),
            }
        )
    return results


def product_get(id: int):
    with _get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, server_id, sku, name, cost_price, uom_inventory, updated_at, company_server_id
            FROM products_local
            WHERE id = ? AND deleted_at IS NULL
            """,
            (id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        product_id, product_server_id, sku, name, cost_price, uom_inventory, updated_at, company_server_id = row
        barcode_row = conn.execute(
            """
            SELECT barcode
            FROM product_barcodes_local
            WHERE product_server_id = ? AND deleted_at IS NULL
            LIMIT 1
            """,
            (product_server_id,),
        ).fetchone()
        return {
            "id": product_id,
            "sku": sku,
            "barcode": barcode_row[0] if barcode_row else "",
            "name": name,
            "unit_cost": cost_price,
            "unit_of_measure": uom_inventory,
            "last_updated": updated_at,
            "company_id": _company_id_by_server_id(conn, company_server_id),
        }


def product_update(
    id: int,
    sku: str,
    barcode: str,
    name: str,
    unit_cost: float,
    unit_of_measure: str,
    last_updated: str,
    company_id: int,
):
    with _get_conn() as conn:
        company = _company_by_id(conn, company_id)
        if not company:
            raise ValueError("company_id invalido")
        company_server_id = company[1]
        now = last_updated or _now()
        product_row = conn.execute(
            "SELECT server_id FROM products_local WHERE id = ? AND deleted_at IS NULL",
            (id,),
        ).fetchone()
        if not product_row:
            return
        product_server_id = product_row[0]
        conn.execute(
            """
            UPDATE products_local
            SET sku = ?, name = ?, cost_price = ?, uom_base = ?, uom_inventory = ?,
                company_server_id = ?, updated_at = ?, synced = 0, synced_at = NULL, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (
                sku,
                name,
                unit_cost,
                unit_of_measure,
                unit_of_measure,
                company_server_id,
                now,
                id,
            ),
        )

        if barcode:
            existing = conn.execute(
                """
                SELECT id FROM product_barcodes_local
                WHERE product_server_id = ? AND deleted_at IS NULL
                ORDER BY id
                LIMIT 1
                """,
                (product_server_id,),
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE product_barcodes_local
                    SET barcode = ?, updated_at = ?, synced = 0, synced_at = NULL, source = 'desktop'
                    WHERE id = ?
                    """,
                    (barcode, now, existing[0]),
                )
            else:
                barcode_uuid = str(uuid4())
                barcode_server_id = _next_local_server_id(conn, "local_server_id_seq_barcodes")
                conn.execute(
                    """
                    INSERT INTO product_barcodes_local (
                      uuid, server_id, company_server_id, product_server_id, barcode,
                      description, is_active, created_at, updated_at, deleted_at,
                      synced, synced_at, source
                    )
                    VALUES (?, ?, ?, ?, ?, NULL, 1, ?, ?, NULL, 0, NULL, 'desktop')
                    """,
                    (
                        barcode_uuid,
                        barcode_server_id,
                        company_server_id,
                        product_server_id,
                        barcode,
                        now,
                        now,
                    ),
                )
        else:
            conn.execute(
                """
                UPDATE product_barcodes_local
                SET deleted_at = ?, is_active = 0, updated_at = ?, synced = 0,
                    synced_at = NULL, source = 'desktop'
                WHERE product_server_id = ? AND deleted_at IS NULL
                """,
                (now, now, product_server_id),
            )
        conn.commit()


def product_delete(id: int):
    with _get_conn() as conn:
        now = _now()
        product_row = conn.execute(
            "SELECT server_id FROM products_local WHERE id = ? AND deleted_at IS NULL",
            (id,),
        ).fetchone()
        if not product_row:
            return
        product_server_id = product_row[0]
        conn.execute(
            """
            UPDATE products_local
            SET deleted_at = ?, is_active = 0, updated_at = ?, synced = 0,
                synced_at = NULL, source = 'desktop'
            WHERE id = ? AND deleted_at IS NULL
            """,
            (now, now, id),
        )
        conn.execute(
            """
            UPDATE product_barcodes_local
            SET deleted_at = ?, is_active = 0, updated_at = ?, synced = 0,
                synced_at = NULL, source = 'desktop'
            WHERE product_server_id = ? AND deleted_at IS NULL
            """,
            (now, now, product_server_id),
        )
        conn.commit()


# -------------------- STOCK LOCATION CRUD --------------------
def stock_location_create(product_id: int, location_id: int, current_stock: float, reorder_point: float):
    raise RuntimeError("Stock_Location nao existe no schema local atual")


def stock_location_get_all():
    raise RuntimeError("Stock_Location nao existe no schema local atual")


def stock_location_get(id: int):
    raise RuntimeError("Stock_Location nao existe no schema local atual")


def stock_location_update(id: int, product_id: int, location_id: int, current_stock: float, reorder_point: float):
    raise RuntimeError("Stock_Location nao existe no schema local atual")


def stock_location_delete(id: int):
    raise RuntimeError("Stock_Location nao existe no schema local atual")


# -------------------- MOVEMENT CRUD --------------------
def movement_create(
    product_id: int,
    location_id: int,
    type_: str,
    quantity: float,
    date_time: str,
    reference: Optional[str],
    user_id: int,
):
    raise RuntimeError("Movement nao existe no schema local atual")


def movement_get_all():
    raise RuntimeError("Movement nao existe no schema local atual")


def movement_get(id: int):
    raise RuntimeError("Movement nao existe no schema local atual")


def movement_update(
    id: int,
    product_id: int,
    location_id: int,
    type_: str,
    quantity: float,
    date_time: str,
    reference: Optional[str],
    user_id: int,
):
    raise RuntimeError("Movement nao existe no schema local atual")


def movement_delete(id: int):
    raise RuntimeError("Movement nao existe no schema local atual")
