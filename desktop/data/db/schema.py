# desktop/data/db/schema.py

"""
Responsabilidade:
- Definir todo o schema SQLite Desktop
- Cache local (offline-first)
- Outbox para Sync Push
- Suporte a Sync Pull incremental
- Incluir:
    - app_meta
    - tabelas locais
    - outbox_local
- Definir SCHEMA_VERSION
"""

SCHEMA_VERSION = 2

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- ======================================================
-- META / CONTROLE LOCAL (NUNCA VAI PARA O SERVIDOR)
-- ======================================================
CREATE TABLE IF NOT EXISTS app_meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);

-- ======================================================
-- CONTEXTO / SESSÃO
-- ======================================================
CREATE TABLE IF NOT EXISTS users_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,
  email TEXT NOT NULL,
  name TEXT,
  role TEXT NOT NULL,
  company_id INTEGER NOT NULL,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS devices_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,
  device_name TEXT,
  os TEXT,
  app_version TEXT,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

-- ======================================================
-- DADOS MESTRE (CACHE LOCAL DA EMPRESA)
-- ======================================================
CREATE TABLE IF NOT EXISTS companies_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  vat_number TEXT,
  is_active INTEGER DEFAULT 1,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS locations_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  code TEXT,
  name TEXT NOT NULL,
  is_active INTEGER DEFAULT 1,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS product_categories_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  code TEXT,
  name TEXT NOT NULL,
  description TEXT,
  is_active INTEGER DEFAULT 1,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS products_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  uom_base TEXT,
  uom_inventory TEXT,
  system_qty REAL,
  serial_number_enabled INTEGER DEFAULT 0,
  is_active INTEGER DEFAULT 1,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS product_barcodes_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  product_uuid TEXT NOT NULL,
  barcode TEXT NOT NULL,
  is_active INTEGER DEFAULT 1,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

-- ======================================================
-- INVENTÁRIO (ESTRUTURA)
-- ======================================================
CREATE TABLE IF NOT EXISTS inventory_events_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  event_type TEXT,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS inventory_event_targets_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  event_uuid TEXT NOT NULL,
  product_uuid TEXT NOT NULL,
  expected_qty REAL DEFAULT 0,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS zones_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,
  event_uuid TEXT NOT NULL,
  name TEXT NOT NULL,
  count_status TEXT,
  lock_status TEXT,

  updated_at DATETIME,
  last_sync_at DATETIME,
  deleted_at DATETIME,
  last_origin TEXT
);

-- ======================================================
-- INVENTÁRIO (OPERAÇÃO OFFLINE / MOBILE / DESKTOP)
-- ======================================================
CREATE TABLE IF NOT EXISTS inventory_items_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,
  zone_uuid TEXT NOT NULL,
  product_uuid TEXT,
  user_uuid TEXT,

  scanned_code TEXT,
  qty_counted REAL DEFAULT 0,
  batch_number TEXT,
  expiry_date TEXT,

  device_timestamp DATETIME,
  server_updated_at DATETIME,

  source TEXT DEFAULT 'desktop',

  synced INTEGER DEFAULT 0,
  synced_at DATETIME,

  last_origin TEXT
);

CREATE TABLE IF NOT EXISTS zone_user_progress_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,
  zone_uuid TEXT NOT NULL,
  user_uuid TEXT NOT NULL,

  started_at DATETIME,
  finished_at DATETIME,
  is_finished INTEGER DEFAULT 0,

  synced INTEGER DEFAULT 0,
  synced_at DATETIME,

  last_origin TEXT
);

-- ======================================================
-- OUTBOX (SINCRONIZAÇÃO PUSH)
-- ======================================================
CREATE TABLE IF NOT EXISTS outbox_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,
  operation TEXT NOT NULL,      -- insert | update | delete
  record_uuid TEXT NOT NULL,
  payload TEXT NOT NULL,        -- JSON
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  attempts INTEGER DEFAULT 0,
  last_error TEXT
);
"""

