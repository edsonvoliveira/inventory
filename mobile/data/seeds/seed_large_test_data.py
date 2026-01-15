# mobile/data/seeds/seed_large_test_data.py

"""
Responsibilities:
- Module responsibilities not classified.
"""

# data_tests_large.py
import sqlite3
import random

try:
    from config.settings import DB_PATH
except ImportError:
    from mobile.config.settings import DB_PATH


def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("🧹 Limpando tabelas...")

    c.executescript("""
        DELETE FROM local_user_profile;
        DELETE FROM local_locations;
        DELETE FROM local_events;
        DELETE FROM local_zones;
        DELETE FROM local_products;
        DELETE FROM local_barcodes;
        DELETE FROM local_inventory_items;
    """)

    # ---------------------------------------------------------------------
    # USER
    # ---------------------------------------------------------------------
    print("👤 Inserindo utilizador admin...")

    c.execute("""
        INSERT INTO local_user_profile (username, password)
        VALUES ('admin', '1234');
    """)

    # ---------------------------------------------------------------------
    # LOCATIONS
    # ---------------------------------------------------------------------
    print("📍 Inserindo 10 locations...")

    locations = []
    for i in range(1, 11):
        locations.append((i, f"Location {i}", f"LC{i:02d}"))

    c.executemany("INSERT INTO local_locations (id, name, code) VALUES (?, ?, ?)",
                  locations)

    # ---------------------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------------------
    print("📅 Inserindo 20 events...")

    events = []
    event_id = 1
    for loc_id in range(1, 11):      # 10 locations
        for j in range(1, 3):        # 2 events por location
            events.append((
                event_id,
                loc_id,
                f"Inventário {loc_id}-{j}",
                "planned"
            ))
            event_id += 1

    c.executemany("""
        INSERT INTO local_events (id, location_id, title, status)
        VALUES (?, ?, ?, ?)
    """, events)

    # ---------------------------------------------------------------------
    # ZONES
    # ---------------------------------------------------------------------
    print("📦 Inserindo 60 zones...")

    zones = []
    zone_id = 1
    for event in events:
        ev_id = event[0]
        # 3 zones por evento → total 20 * 3 = 60
        for z in range(1, 4):
            zones.append((zone_id, ev_id, f"Zona {ev_id}-{z}"))
            zone_id += 1

    c.executemany("""
        INSERT INTO local_zones (id, event_id, name)
        VALUES (?, ?, ?)
    """, zones)

    # ---------------------------------------------------------------------
    # PRODUCTS
    # ---------------------------------------------------------------------
    print("📦 Inserindo 80 products...")

    products = []
    for i in range(1, 81):
        products.append((
            i,
            f"SKU-{i:04d}",
            f"Produto {i}",
            random.choice(["UN", "CX", "LT", "KG", "PAR"])
        ))

    c.executemany("""
        INSERT INTO local_products (id, sku, name, uom_inventory)
        VALUES (?, ?, ?, ?)
    """, products)

    # ---------------------------------------------------------------------
    # BARCODES
    # ---------------------------------------------------------------------
    print("🏷 Inserindo 160 barcodes... (2 por produto)")

    barcodes = []
    barcode_id = 1

    for product in products:
        pid = product[0]

        # gerar dois barcodes válidos (fakes mas plausíveis)
        for _ in range(2):
            fake_code = "56" + str(random.randint(10**11, 10**12 - 1))
            barcodes.append((barcode_id, pid, fake_code))
            barcode_id += 1

    c.executemany("""
        INSERT INTO local_barcodes (id, product_id, barcode)
        VALUES (?, ?, ?)
    """, barcodes)

    # ---------------------------------------------------------------------
    # inventory_items → VAZIO
    # ---------------------------------------------------------------------
    print("📝 inventory_items deixado vazio (como solicitado).")

    conn.commit()
    conn.close()

    print("✅ BASE DE TESTES AMPLIADA GERADA COM SUCESSO!")
    print("   Users → admin / 1234")
    print("   Locations → 10")
    print("   Events → 20")
    print("   Zones → 60")
    print("   Products → 80")
    print("   Barcodes → 160")
    print("   Inventory items → 0")

if __name__ == "__main__":
    seed()
