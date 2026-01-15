import sqlite3


def seed_minimal_data(conn: sqlite3.Connection) -> None:
    # Companies
    conn.execute(
        "INSERT OR IGNORE INTO companies_local (uuid, server_id, name, is_active, updated_at) VALUES (?, ?, ?, ?, ?)",
        ("company-uuid-1", 1, "Empresa Demo", 1, "2024-01-01T00:00:00"),
    )

    # Users
    conn.execute(
        "INSERT OR IGNORE INTO users_local (uuid, server_id, company_server_id, name, role, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("user-uuid-1", 1, 1, "Operador Demo", "Operador", 1, "2024-01-01T00:00:00"),
    )

    # Locations
    conn.execute(
        "INSERT OR IGNORE INTO locations_local (uuid, server_id, company_server_id, code, name, address, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("loc-uuid-1", 1, 1, "LOC-01", "Armazém Central", "Rua A", 1, "2024-01-01T00:00:00"),
    )

    # Events
    conn.execute(
        "INSERT OR IGNORE INTO inventory_events_local (uuid, server_id, company_server_id, location_server_id, title, event_type, status, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("evt-uuid-1", 1, 1, 1, "Inventário Janeiro", "cycle_count", "planned", "2024-01-01T00:00:00"),
    )

    # Zones
    conn.execute(
        "INSERT OR IGNORE INTO zones_local (uuid, server_id, event_uuid, event_server_id, name, count_status, lock_status, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("zone-uuid-1", 1, "evt-uuid-1", 1, "Zona A", "not_started", "unlocked", 1, "2024-01-01T00:00:00"),
    )

    # Products
    conn.execute(
        "INSERT OR IGNORE INTO products_local (uuid, server_id, company_server_id, sku, name, uom_inventory, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("prod-uuid-1", 1, 1, "SKU-001", "Produto A", "UN", 1, "2024-01-01T00:00:00"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO products_local (uuid, server_id, company_server_id, sku, name, uom_inventory, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("prod-uuid-2", 2, 1, "SKU-002", "Produto B", "UN", 1, "2024-01-01T00:00:00"),
    )

    # Barcodes
    conn.execute(
        "INSERT OR IGNORE INTO product_barcodes_local (uuid, server_id, company_server_id, product_uuid, product_server_id, barcode, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("barcode-uuid-1", 1, 1, "prod-uuid-1", 1, "789000000001", 1, "2024-01-01T00:00:00"),
    )
