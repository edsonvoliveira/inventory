# desktop/data/db/schema.py

"""
Responsabilities:
- Define entire SQLite Desktop schema
- Desktop as System of Record (SoR)
- Server as authority only for identity (companies, users)
- Offline-first + Async Sync
- Local cache (offline-first)
- Outbox for Sync Push
- Support incremental Sync Pull
- Include:
    - app_meta
    - local tables (master cache + structure + operation)
    - outbox_local
- Define SCHEMA_VERSION
"""

SCHEMA_VERSION = 5

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- ======================================================
-- META
-- ======================================================
CREATE TABLE IF NOT EXISTS app_meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);

-- ======================================================
-- IDENTITY (SERVER OWNED)
-- ======================================================
CREATE TABLE IF NOT EXISTS users_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  email TEXT NOT NULL,
  username TEXT,
  name TEXT,
  role TEXT NOT NULL,

  company_server_id INTEGER NOT NULL,
  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  last_sync_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_users_local_uuid ON users_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_users_local_server_id ON users_local(server_id);

CREATE TABLE IF NOT EXISTS companies_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  name TEXT NOT NULL,
  vat_number TEXT,
  country_code TEXT,
  address TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_companies_local_uuid ON companies_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_companies_local_server_id ON companies_local(server_id);

-- ======================================================
-- MASTER DATA (DESKTOP = SoR)
-- ======================================================
CREATE TABLE IF NOT EXISTS locations_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  company_server_id INTEGER NOT NULL,
  code TEXT,
  name TEXT NOT NULL,
  address TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

CREATE TABLE IF NOT EXISTS product_categories_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  company_server_id INTEGER NOT NULL,
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

CREATE TABLE IF NOT EXISTS products_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  company_server_id INTEGER NOT NULL,
  category_server_id INTEGER,

  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,

  uom_base TEXT,
  uom_inventory TEXT,
  conversion_factor REAL DEFAULT 1,

  system_qty REAL DEFAULT 0,
  cost_price REAL,

  is_sensitive INTEGER DEFAULT 0,
  serial_number_enabled INTEGER DEFAULT 0,
  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

CREATE TABLE IF NOT EXISTS product_barcodes_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  company_server_id INTEGER NOT NULL,
  product_server_id INTEGER NOT NULL,

  barcode TEXT NOT NULL,
  description TEXT,
  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

-- ======================================================
-- INVENTORY STRUCTURE
-- ======================================================
CREATE TABLE IF NOT EXISTS inventory_events_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  company_server_id INTEGER NOT NULL,
  location_server_id INTEGER NOT NULL,

  title TEXT NOT NULL,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,

  required_counts INTEGER,
  required_audits INTEGER,
  tolerance_percent REAL,
  tolerance_absolute REAL,

  primary_finished_at TEXT,
  audit_finished_at TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

CREATE TABLE IF NOT EXISTS inventory_event_targets_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  company_server_id INTEGER NOT NULL,
  event_server_id INTEGER NOT NULL,
  product_server_id INTEGER NOT NULL,

  expected_qty REAL DEFAULT 0,
  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

CREATE TABLE IF NOT EXISTS zones_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  event_server_id INTEGER NOT NULL,

  name TEXT NOT NULL,
  description TEXT,
  count_status TEXT DEFAULT 'not_started',
  lock_status TEXT DEFAULT 'unlocked',

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

-- ======================================================
-- INVENTORY OPERATION
-- ======================================================
CREATE TABLE IF NOT EXISTS inventory_items_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  zone_server_id INTEGER NOT NULL,
  product_server_id INTEGER,
  user_server_id INTEGER,
  created_by_user_server_id INTEGER,

  scanned_code TEXT,
  qty_counted REAL DEFAULT 0,
  batch_number TEXT,
  expiry_date TEXT,
  is_new_product INTEGER DEFAULT 0,

  device_timestamp TEXT,
  server_timestamp TEXT,

  device_id TEXT,
  latitude REAL,
  longitude REAL,

  source TEXT DEFAULT 'desktop',
  audit_meta TEXT,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT
);

CREATE TABLE IF NOT EXISTS zone_user_progress_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  zone_server_id INTEGER NOT NULL,
  user_server_id INTEGER NOT NULL,

  count_type TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  is_finished INTEGER DEFAULT 0,

  items_counted INTEGER DEFAULT 0,
  qty_total REAL DEFAULT 0,

  device_id TEXT,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  source TEXT DEFAULT 'desktop',
  synced INTEGER DEFAULT 0,
  synced_at TEXT
);

-- ======================================================
-- AUDIT / DIVERGENCE / WORKFLOW
-- ======================================================
CREATE TABLE IF NOT EXISTS divergence_reason_types_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  company_server_id INTEGER NOT NULL,
  code TEXT NOT NULL,
  description TEXT NOT NULL,
  requires_documentation INTEGER DEFAULT 0,

  is_active INTEGER DEFAULT 1,
  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

CREATE TABLE IF NOT EXISTS inventory_divergences_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  event_server_id INTEGER NOT NULL,
  zone_server_id INTEGER,
  product_server_id INTEGER NOT NULL,

  qty_primary REAL,
  qty_audit REAL,
  difference REAL,

  resolution TEXT,
  divergence_reason TEXT,
  resolved_by_user_server_id INTEGER,
  resolved_at TEXT,

  metadata TEXT,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

CREATE TABLE IF NOT EXISTS workflow_logs_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  entity TEXT NOT NULL,
  entity_server_id INTEGER NOT NULL,
  from_state TEXT,
  to_state TEXT,
  triggered_by_user_server_id INTEGER,
  timestamp TEXT NOT NULL,

  synced INTEGER DEFAULT 0,
  synced_at TEXT,
  source TEXT DEFAULT 'desktop'
);

-- ======================================================
-- OUTBOX
-- ======================================================
CREATE TABLE IF NOT EXISTS outbox_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,
  operation TEXT NOT NULL,
  record_uuid TEXT NOT NULL,
  payload TEXT NOT NULL,

  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  attempts INTEGER DEFAULT 0,
  last_error TEXT
);
"""


