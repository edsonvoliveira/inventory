# desktop/data/db/schema.py

"""
Responsabilidade:
- Definir todo o schema SQLite Desktop
- Cache local (offline-first)
- Outbox para Sync Push
- Suporte a Sync Pull incremental
- Incluir:
    - app_meta
    - tabelas locais (cache master + estrutura + operação)
    - outbox_local
- Definir SCHEMA_VERSION
"""

SCHEMA_VERSION = 3

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
-- CONTEXTO / SESSÃO (USADO PELO APP; NÃO É "MASTER" COMPLETO)
-- ======================================================
CREATE TABLE IF NOT EXISTS users_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  email TEXT NOT NULL,
  username TEXT,
  name TEXT,
  role TEXT NOT NULL,

  company_server_id INTEGER NOT NULL,     -- server_id da empresa
  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  last_sync_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_users_local_uuid ON users_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_users_local_server_id ON users_local(server_id);

CREATE TABLE IF NOT EXISTS devices_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  device_uuid TEXT,            -- identificador do device (se aplicável)
  device_name TEXT,
  os TEXT,
  app_version TEXT,

  is_blocked INTEGER DEFAULT 0,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  last_sync_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_devices_local_uuid ON devices_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_devices_local_server_id ON devices_local(server_id);

-- ======================================================
-- DADOS MESTRE (CACHE LOCAL DA EMPRESA)
-- ======================================================
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

CREATE TABLE IF NOT EXISTS locations_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  company_server_id INTEGER NOT NULL,

  code TEXT,
  name TEXT NOT NULL,
  address TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_locations_local_uuid ON locations_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_locations_local_server_id ON locations_local(server_id);

CREATE TABLE IF NOT EXISTS product_categories_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  company_server_id INTEGER NOT NULL,

  code TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_product_categories_local_uuid ON product_categories_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_product_categories_local_server_id ON product_categories_local(server_id);

CREATE TABLE IF NOT EXISTS products_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  company_server_id INTEGER NOT NULL,
  category_server_id INTEGER,           -- pode ser NULL

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

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_products_local_uuid ON products_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_products_local_server_id ON products_local(server_id);
CREATE INDEX IF NOT EXISTS ix_products_local_sku ON products_local(sku);

CREATE TABLE IF NOT EXISTS product_barcodes_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  company_server_id INTEGER NOT NULL,
  product_server_id INTEGER NOT NULL,

  barcode TEXT NOT NULL,
  description TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_product_barcodes_local_uuid ON product_barcodes_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_product_barcodes_local_server_id ON product_barcodes_local(server_id);
CREATE INDEX IF NOT EXISTS ix_product_barcodes_local_barcode ON product_barcodes_local(barcode);

-- ======================================================
-- INVENTÁRIO (ESTRUTURA)
-- ======================================================
CREATE TABLE IF NOT EXISTS inventory_events_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  company_server_id INTEGER NOT NULL,
  location_server_id INTEGER NOT NULL,

  title TEXT NOT NULL,
  event_type TEXT,
  status TEXT NOT NULL,

  required_counts INTEGER,
  required_audits INTEGER,
  tolerance_percent REAL,
  tolerance_absolute REAL,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_events_local_uuid ON inventory_events_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_events_local_server_id ON inventory_events_local(server_id);

CREATE TABLE IF NOT EXISTS inventory_event_targets_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  company_server_id INTEGER NOT NULL,
  event_server_id INTEGER NOT NULL,
  product_server_id INTEGER NOT NULL,

  expected_qty REAL DEFAULT 0,
  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_event_targets_local_uuid ON inventory_event_targets_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_event_targets_local_server_id ON inventory_event_targets_local(server_id);

CREATE TABLE IF NOT EXISTS zones_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER NOT NULL,

  event_server_id INTEGER NOT NULL,

  name TEXT NOT NULL,
  description TEXT,

  count_status TEXT,
  lock_status TEXT,

  is_active INTEGER DEFAULT 1,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 1,
  synced_at TEXT,
  source TEXT DEFAULT 'server'
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_zones_local_uuid ON zones_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_zones_local_server_id ON zones_local(server_id);

-- ======================================================
-- INVENTÁRIO (OPERAÇÃO OFFLINE)
-- ======================================================
CREATE TABLE IF NOT EXISTS inventory_items_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  zone_server_id INTEGER NOT NULL,
  product_server_id INTEGER,
  user_server_id INTEGER,

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

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER DEFAULT 0,
  synced_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_items_local_uuid ON inventory_items_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_items_local_server_id ON inventory_items_local(server_id);
CREATE INDEX IF NOT EXISTS ix_inventory_items_local_zone_server_id ON inventory_items_local(zone_server_id);

CREATE TABLE IF NOT EXISTS zone_user_progress_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL,
  server_id INTEGER,

  zone_server_id INTEGER NOT NULL,
  user_server_id INTEGER NOT NULL,

  count_type TEXT,           -- primary / audit
  started_at TEXT,
  finished_at TEXT,
  is_finished INTEGER DEFAULT 0,

  items_counted INTEGER DEFAULT 0,
  qty_total REAL DEFAULT 0,

  device_id TEXT,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  source TEXT DEFAULT 'mobile',

  synced INTEGER DEFAULT 0,
  synced_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_zone_user_progress_local_uuid ON zone_user_progress_local(uuid);
CREATE UNIQUE INDEX IF NOT EXISTS ux_zone_user_progress_local_server_id ON zone_user_progress_local(server_id);
CREATE INDEX IF NOT EXISTS ix_zone_user_progress_local_zone_server_id ON zone_user_progress_local(zone_server_id);

-- ======================================================
-- OUTBOX (SINCRONIZAÇÃO PUSH)
-- ======================================================
CREATE TABLE IF NOT EXISTS outbox_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,
  operation TEXT NOT NULL,      -- insert | update | delete
  record_uuid TEXT NOT NULL,
  payload TEXT NOT NULL,        -- JSON serializado (string)

  created_at TEXT DEFAULT CURRENT_TIMESTAMP,

  attempts INTEGER DEFAULT 0,
  last_error TEXT
);
CREATE INDEX IF NOT EXISTS ix_outbox_local_table_op ON outbox_local(table_name, operation);
CREATE INDEX IF NOT EXISTS ix_outbox_local_record_uuid ON outbox_local(record_uuid);
"""
