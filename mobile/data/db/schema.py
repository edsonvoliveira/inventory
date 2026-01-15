# mobile/data/db/schema.py

"""
Responsibilities:
- Define database schema and versioning.
- Provide SQL statements for setup.
"""

SCHEMA_VERSION = 3

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- ======================================================
-- META / CONTROLE LOCAL
-- ======================================================
CREATE TABLE IF NOT EXISTS app_meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);

-- Controle técnico do sync (cursors por tabela)
CREATE TABLE IF NOT EXISTS sync_state (
  key TEXT PRIMARY KEY,          -- ex: pull_cursor_products, pull_cursor_events
  value TEXT NOT NULL            -- ex: ISO timestamp, ou token/etag
);

-- ======================================================
-- IDENTIDADE / CONTEXTO MÍNIMO (READ-ONLY via Pull)
-- ======================================================
CREATE TABLE IF NOT EXISTS companies_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,
  name TEXT NOT NULL,
  is_active INTEGER DEFAULT 1,
  updated_at TEXT,
  deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS users_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,
  company_server_id INTEGER NOT NULL,

  name TEXT NOT NULL,
  role TEXT NOT NULL,
  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_users_local_company_server_id ON users_local(company_server_id);

CREATE TABLE IF NOT EXISTS devices_local (
  uuid TEXT PRIMARY KEY,                 -- uuid local do registo de device
  server_id INTEGER UNIQUE,              -- id no server (quando existir)
  device_uuid TEXT NOT NULL UNIQUE,      -- id estável do hardware
  os TEXT,
  app_version TEXT,
  is_blocked INTEGER DEFAULT 0,
  last_sync_at TEXT,
  updated_at TEXT,
  deleted_at TEXT
);

-- ======================================================
-- CACHE OPERACIONAL (MAIORIA READ-ONLY via Pull)
-- ======================================================

CREATE TABLE IF NOT EXISTS locations_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,

  company_server_id INTEGER NOT NULL,

  code TEXT,
  name TEXT NOT NULL,
  address TEXT,

  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_locations_local_company_server_id ON locations_local(company_server_id);

CREATE TABLE IF NOT EXISTS inventory_events_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,

  company_server_id INTEGER NOT NULL,
  location_server_id INTEGER NOT NULL,

  title TEXT NOT NULL,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,

  required_counts INTEGER DEFAULT 1,
  required_audits INTEGER,
  tolerance_percent REAL,
  tolerance_absolute REAL,

  primary_finished_at TEXT,
  audit_finished_at TEXT,

  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_events_local_company_server_id ON inventory_events_local(company_server_id);
CREATE INDEX IF NOT EXISTS ix_events_local_location_server_id ON inventory_events_local(location_server_id);
CREATE INDEX IF NOT EXISTS ix_events_local_status ON inventory_events_local(status);

CREATE TABLE IF NOT EXISTS zones_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,

  event_uuid TEXT NOT NULL,
  event_server_id INTEGER NOT NULL,

  name TEXT NOT NULL,
  description TEXT,

  count_status TEXT,
  lock_status TEXT,
  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_zones_local_event_uuid ON zones_local(event_uuid);
CREATE INDEX IF NOT EXISTS ix_zones_local_event_server_id ON zones_local(event_server_id);
CREATE INDEX IF NOT EXISTS ix_zones_local_status ON zones_local(count_status, lock_status);

CREATE TABLE IF NOT EXISTS inventory_event_targets_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,

  company_server_id INTEGER NOT NULL,

  event_uuid TEXT NOT NULL,
  event_server_id INTEGER NOT NULL,

  product_uuid TEXT NOT NULL,
  product_server_id INTEGER NOT NULL,

  expected_qty REAL DEFAULT 0,
  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_targets_local_event_uuid ON inventory_event_targets_local(event_uuid);
CREATE INDEX IF NOT EXISTS ix_targets_local_product_uuid ON inventory_event_targets_local(product_uuid);

-- ======================================================
-- CATÁLOGO (SUPORTE “TOTAL” para operação)
-- products + barcodes devem ser completos (ou o mais completo possível).
-- ======================================================

CREATE TABLE IF NOT EXISTS product_categories_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,

  company_server_id INTEGER NOT NULL,

  code TEXT,
  name TEXT NOT NULL,
  description TEXT,

  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_product_categories_local_company_server_id ON product_categories_local(company_server_id);
CREATE INDEX IF NOT EXISTS ix_product_categories_local_name ON product_categories_local(name);


CREATE TABLE IF NOT EXISTS products_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,

  company_server_id INTEGER NOT NULL,
  category_server_id INTEGER,

  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,

  uom_base TEXT,
  uom_inventory TEXT,
  conversion_factor REAL DEFAULT 1,

  system_qty REAL DEFAULT 0,

  is_sensitive INTEGER DEFAULT 0,
  serial_number_enabled INTEGER DEFAULT 0,
  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_products_local_company_server_id ON products_local(company_server_id);
CREATE INDEX IF NOT EXISTS ix_products_local_sku ON products_local(sku);
CREATE INDEX IF NOT EXISTS ix_products_local_name ON products_local(name);

CREATE TABLE IF NOT EXISTS product_barcodes_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE,

  company_server_id INTEGER NOT NULL,

  product_uuid TEXT NOT NULL,
  product_server_id INTEGER NOT NULL,

  barcode TEXT NOT NULL,
  description TEXT,

  is_active INTEGER DEFAULT 1,

  updated_at TEXT,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_barcodes_local_barcode ON product_barcodes_local(barcode);
CREATE INDEX IF NOT EXISTS ix_barcodes_local_product_uuid ON product_barcodes_local(product_uuid);

-- ======================================================
-- OPERAÇÃO OFFLINE (WRITE)
-- Aqui está o “coração” do mobile.
-- ======================================================

CREATE TABLE IF NOT EXISTS inventory_items_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER UNIQUE,                  -- preenchido após ACK do server

  event_uuid TEXT NOT NULL,
  event_server_id INTEGER NOT NULL,

  zone_uuid TEXT NOT NULL,
  zone_server_id INTEGER NOT NULL,

  user_uuid TEXT NOT NULL,
  user_server_id INTEGER NOT NULL,

  -- referência de produto (quando resolvido no catálogo)
  product_uuid TEXT,
  product_server_id INTEGER,

  -- scanner e fallback
  scanned_code TEXT,
  manual_sku TEXT,
  manual_name TEXT,

  qty_counted REAL NOT NULL DEFAULT 0,
  batch_number TEXT,
  expiry_date TEXT,

  -- regras operacionais
  is_new_product INTEGER DEFAULT 0,          -- fora do target
  unknown_product INTEGER DEFAULT 0,         -- não encontrou no catálogo local

  -- snapshot do estado do produto no momento da contagem (para auditoria)
  product_is_active_at_count INTEGER,        -- 0/1 (se houver product)
  product_name_at_count TEXT,
  product_sku_at_count TEXT,

  -- auditoria técnica
  device_timestamp TEXT NOT NULL,
  server_timestamp TEXT,

  device_id TEXT,                            -- device_uuid
  latitude REAL,
  longitude REAL,

  source TEXT NOT NULL DEFAULT 'mobile',
  audit_meta TEXT,                           -- JSON string (leve)

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  synced INTEGER NOT NULL DEFAULT 0,
  synced_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_items_local_event_server_id ON inventory_items_local(event_server_id);
CREATE INDEX IF NOT EXISTS ix_items_local_zone_server_id  ON inventory_items_local(zone_server_id);
CREATE INDEX IF NOT EXISTS ix_items_local_product_server_id ON inventory_items_local(product_server_id);
CREATE INDEX IF NOT EXISTS ix_items_local_scanned_code ON inventory_items_local(scanned_code);
CREATE INDEX IF NOT EXISTS ix_items_local_synced ON inventory_items_local(synced);

CREATE TABLE IF NOT EXISTS zone_user_progress_local (
  uuid TEXT PRIMARY KEY,
  server_id INTEGER UNIQUE,                  -- preenchido após ACK do server

  event_uuid TEXT NOT NULL,
  event_server_id INTEGER NOT NULL,

  zone_uuid TEXT NOT NULL,
  zone_server_id INTEGER NOT NULL,

  user_uuid TEXT NOT NULL,
  user_server_id INTEGER NOT NULL,

  count_type TEXT NOT NULL,                  -- primary / audit
  started_at TEXT NOT NULL,
  finished_at TEXT,
  is_finished INTEGER DEFAULT 0,

  items_counted INTEGER DEFAULT 0,
  qty_total REAL DEFAULT 0,

  device_id TEXT,

  created_at TEXT,
  updated_at TEXT,
  deleted_at TEXT,

  source TEXT NOT NULL DEFAULT 'mobile',

  synced INTEGER NOT NULL DEFAULT 0,
  synced_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_progress_local_zone_server_id ON zone_user_progress_local(zone_server_id);
CREATE INDEX IF NOT EXISTS ix_progress_local_user_server_id ON zone_user_progress_local(user_server_id);
CREATE INDEX IF NOT EXISTS ix_progress_local_synced ON zone_user_progress_local(synced);

-- ======================================================
-- OUTBOX (PUSH)
-- ======================================================
CREATE TABLE IF NOT EXISTS outbox_local (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  table_name TEXT NOT NULL,        -- inventory_items / zone_user_progress
  operation TEXT NOT NULL,         -- insert | update | delete(soft)
  record_uuid TEXT NOT NULL,
  payload TEXT NOT NULL,           -- JSON serializado

  created_at TEXT DEFAULT CURRENT_TIMESTAMP,

  attempts INTEGER DEFAULT 0,
  last_error TEXT
);
CREATE INDEX IF NOT EXISTS ix_outbox_local_table_op ON outbox_local(table_name, operation);
CREATE INDEX IF NOT EXISTS ix_outbox_local_record_uuid ON outbox_local(record_uuid);
"""
