# mobile/data/db/schema.py

SCHEMA_VERSION = 1

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- ======================================================
-- META / CONTROLE LOCAL
-- ======================================================
CREATE TABLE IF NOT EXISTS app_meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);

-- ======================================================
-- CACHE MÍNIMO (READ-ONLY)
-- ======================================================
CREATE TABLE IF NOT EXISTS companies_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL,
  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS product_barcodes_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL,
  product_uuid TEXT NOT NULL,
  barcode TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory_events_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory_event_targets_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL,
  event_uuid TEXT NOT NULL,
  product_uuid TEXT NOT NULL,
  expected_qty REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS zones_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL,
  event_uuid TEXT NOT NULL,
  name TEXT NOT NULL,
  count_status TEXT,
  lock_status TEXT
);

-- ======================================================
-- OPERAÇÃO OFFLINE (WRITE)
-- ======================================================
CREATE TABLE IF NOT EXISTS inventory_items_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER,
  zone_uuid TEXT NOT NULL,
  product_uuid TEXT,
  scanned_code TEXT,
  qty_counted REAL DEFAULT 0,
  batch_number TEXT,
  expiry_date TEXT,
  device_timestamp TEXT,
  synced INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS zone_user_progress_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER,
  zone_uuid TEXT NOT NULL,
  user_uuid TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  is_finished INTEGER DEFAULT 0,
  synced INTEGER DEFAULT 0
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
