-- -------------------------------------------------------------------
-- SCHEMA FINALIZADO (V7 - REVISADO)
-- Melhores práticas: tipos schema-qualified, índices para RLS, NOT NULL para created_at,
-- funções helper SECURITY DEFINER com search_path, triggers para updated_at.
-- -------------------------------------------------------------------

-- 0) TIPOS ENUM (idempotente e schema-qualified)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_type t
    JOIN pg_namespace n ON t.typnamespace = n.oid
    WHERE t.typname = 'user_role' AND n.nspname = 'public'
  ) THEN
    CREATE TYPE public.user_role AS ENUM ('admin', 'manager', 'coordinator', 'auditor', 'counter');
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM pg_type t
    JOIN pg_namespace n ON t.typnamespace = n.oid
    WHERE t.typname = 'event_status' AND n.nspname = 'public'
  ) THEN
    CREATE TYPE public.event_status AS ENUM ('planned', 'open', 'counting', 'closed', 'finalized');
  END IF;
END
$$;


-- 1) MASTER DATA TABLES

CREATE TABLE IF NOT EXISTS public.companies (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name varchar(100) NOT NULL,
  document varchar(15),
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.users (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_id integer NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  supabase_auth_id uuid UNIQUE, -- pode ser NOT NULL se sempre mapeado a Auth
  username varchar(100) UNIQUE NOT NULL,
  password_hash varchar(255) NOT NULL,
  name varchar(100),
  role public.user_role NOT NULL DEFAULT 'auditor',
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_company_username ON public.users(company_id, username);
CREATE INDEX IF NOT EXISTS idx_users_company ON public.users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_supabase_auth_id ON public.users(supabase_auth_id);


CREATE TABLE IF NOT EXISTS public.locations (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_id integer NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  code varchar(15),
  name varchar(50) NOT NULL,
  address text,
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_locations_company ON public.locations(company_id);


CREATE TABLE IF NOT EXISTS public.categories (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_id integer NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  code varchar(20) NOT NULL,
  name varchar(50) NOT NULL,
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_company_code ON public.categories(company_id, code);
CREATE INDEX IF NOT EXISTS idx_categories_company ON public.categories(company_id);


CREATE TABLE IF NOT EXISTS public.products (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_id integer NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  category_id integer REFERENCES public.categories(id) ON DELETE SET NULL,
  sku varchar(30) NOT NULL,
  name varchar(80) NOT NULL,
  description text,
  uom_base varchar(5) NOT NULL DEFAULT 'UN',
  uom_inventory varchar(5) NOT NULL DEFAULT 'UN',
  conversion_factor numeric(12,2) NOT NULL DEFAULT 1.00,
  default_location_info varchar(30),
  system_qty numeric(12,2) NOT NULL DEFAULT 0.00,
  cost_price numeric(12,2),
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_products_company_sku ON public.products(company_id, sku);
CREATE INDEX IF NOT EXISTS idx_products_company ON public.products(company_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON public.products(sku);


CREATE TABLE IF NOT EXISTS public.product_barcodes (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_id integer NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  product_id integer NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
  barcode varchar(20) NOT NULL,
  description varchar(50),
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_barcodes_company_barcode ON public.product_barcodes(company_id, barcode);
CREATE INDEX IF NOT EXISTS idx_barcodes_product ON public.product_barcodes(product_id);


-- 2) INVENTORY EVENTS

CREATE TABLE IF NOT EXISTS public.inventory_events (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_id integer NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  location_id integer NOT NULL REFERENCES public.locations(id) ON DELETE CASCADE,
  title varchar(50) NOT NULL,
  status public.event_status NOT NULL DEFAULT 'planned',
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_inventory_events_company ON public.inventory_events(company_id);
CREATE INDEX IF NOT EXISTS idx_inventory_events_location ON public.inventory_events(location_id);


CREATE TABLE IF NOT EXISTS public.inventory_event_targets (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_id integer NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  event_id integer NOT NULL REFERENCES public.inventory_events(id) ON DELETE CASCADE,
  product_id integer NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
  expected_qty numeric(12,2) NOT NULL DEFAULT 0.00,
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_targets_event_product ON public.inventory_event_targets(event_id, product_id);
CREATE INDEX IF NOT EXISTS idx_targets_company ON public.inventory_event_targets(company_id);


CREATE TABLE IF NOT EXISTS public.zones (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  event_id integer NOT NULL REFERENCES public.inventory_events(id) ON DELETE CASCADE,
  name varchar(30) NOT NULL,
  is_active boolean NOT NULL DEFAULT TRUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_zones_event ON public.zones(event_id);


-- 3) INVENTORY ITEMS

CREATE TABLE IF NOT EXISTS public.inventory_items (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  zone_id integer NOT NULL REFERENCES public.zones(id) ON DELETE CASCADE,
  user_id integer REFERENCES public.users(id) ON DELETE SET NULL,
  product_id integer REFERENCES public.products(id) ON DELETE SET NULL,
  scanned_code varchar(50) NOT NULL,
  qty_counted numeric(12,3) NOT NULL,
  batch_number varchar(100),
  expiry_date date,
  is_new_product boolean NOT NULL DEFAULT FALSE,
  notes text,
  is_active boolean NOT NULL DEFAULT TRUE,
  device_timestamp timestamptz NOT NULL,
  server_timestamp timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_items_zone ON public.inventory_items(zone_id);
CREATE INDEX IF NOT EXISTS idx_items_product ON public.inventory_items(product_id);
CREATE INDEX IF NOT EXISTS idx_items_user ON public.inventory_items(user_id);
CREATE INDEX IF NOT EXISTS idx_items_scanned_code ON public.inventory_items(scanned_code);


-- 4) TRIGGER TO AUTO-UPDATE updated_at

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

-- create triggers on tables that have updated_at column
DO $$
DECLARE
  r RECORD;
  trg TEXT;
BEGIN
  FOR r IN
    SELECT table_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND column_name = 'updated_at'
  LOOP
    trg := 'trg_' || r.table_name || '_updated_at';
    EXECUTE format('DROP TRIGGER IF EXISTS %I ON public.%I', trg, r.table_name);
    EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE ON public.%I FOR EACH ROW EXECUTE PROCEDURE public.update_updated_at_column()', trg, r.table_name);
  END LOOP;
END$$;


-- 5) RLS HELPER FUNCTIONS (SECURITY DEFINER, STABLE)

CREATE OR REPLACE FUNCTION public.get_auth_company_id()
RETURNS integer
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT company_id
  FROM public.users
  WHERE supabase_auth_id = auth.uid()
  LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION public.get_auth_user_role()
RETURNS public.user_role
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT role
  FROM public.users
  WHERE supabase_auth_id = auth.uid()
  LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION public.get_auth_user_pk_id()
RETURNS integer
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT id
  FROM public.users
  WHERE supabase_auth_id = auth.uid()
  LIMIT 1;
$$;

-- Revoke execute from anon and authenticated to prevent callers invoking directly.
REVOKE EXECUTE ON FUNCTION public.get_auth_company_id() FROM anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.get_auth_user_role() FROM anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.get_auth_user_pk_id() FROM anon, authenticated;


-- 6) ENABLE RLS on tables (idempotent)
ALTER TABLE IF EXISTS public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.product_barcodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.inventory_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.inventory_event_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.zones ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.inventory_items ENABLE ROW LEVEL SECURITY;


-- 7) RLS POLICIES (multi-tenant)

-- 7.1 companies
CREATE POLICY IF NOT EXISTS companies_read_by_company_id
ON public.companies
FOR SELECT
TO authenticated
USING ( id = public.get_auth_company_id() );

CREATE POLICY IF NOT EXISTS companies_admin_manage
ON public.companies
FOR ALL
TO authenticated
USING (
  id = public.get_auth_company_id()
  AND public.get_auth_user_role() = 'admin'
)
WITH CHECK (
  NEW.id = public.get_auth_company_id()
  AND public.get_auth_user_role() = 'admin'
);


-- 7.2 users
CREATE POLICY IF NOT EXISTS users_read_all_in_company
ON public.users
FOR SELECT
TO authenticated
USING ( company_id = public.get_auth_company_id() );

CREATE POLICY IF NOT EXISTS users_admin_manage
ON public.users
FOR ALL
TO authenticated
USING (
  company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() = 'admin'
)
WITH CHECK (
  NEW.company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() = 'admin'
);


-- 7.3 locations
CREATE POLICY IF NOT EXISTS locations_read_company
ON public.locations
FOR SELECT
TO authenticated
USING ( company_id = public.get_auth_company_id() );

CREATE POLICY IF NOT EXISTS locations_admin_manager_manage
ON public.locations
FOR ALL
TO authenticated
USING (
  company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager')
)
WITH CHECK (
  NEW.company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager')
);


-- 7.4 categories
CREATE POLICY IF NOT EXISTS categories_read_company
ON public.categories
FOR SELECT
TO authenticated
USING ( company_id = public.get_auth_company_id() );

CREATE POLICY IF NOT EXISTS categories_admin_manager_manage
ON public.categories
FOR ALL
TO authenticated
USING (
  company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager')
)
WITH CHECK (
  NEW.company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager')
);


-- 7.5 products
CREATE POLICY IF NOT EXISTS products_read_company
ON public.products
FOR SELECT
TO authenticated
USING ( company_id = public.get_auth_company_id() );

CREATE POLICY IF NOT EXISTS products_manager_auditor_manage
ON public.products
FOR ALL
TO authenticated
USING (
  company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','auditor')
)
WITH CHECK (
  NEW.company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','auditor')
);


-- 7.6 product_barcodes
CREATE POLICY IF NOT EXISTS barcodes_read_company
ON public.product_barcodes
FOR SELECT
TO authenticated
USING ( company_id = public.get_auth_company_id() );

CREATE POLICY IF NOT EXISTS barcodes_manager_auditor_manage
ON public.product_barcodes
FOR ALL
TO authenticated
USING (
  company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','auditor')
)
WITH CHECK (
  NEW.company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','auditor')
);


-- 7.7 inventory_events
CREATE POLICY IF NOT EXISTS events_management_roles
ON public.inventory_events
FOR ALL
TO authenticated
USING (
  company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
)
WITH CHECK (
  NEW.company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
);


-- 7.8 inventory_event_targets
CREATE POLICY IF NOT EXISTS targets_management_roles
ON public.inventory_event_targets
FOR ALL
TO authenticated
USING (
  company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
)
WITH CHECK (
  NEW.company_id = public.get_auth_company_id()
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
);


-- 7.9 zones
CREATE POLICY IF NOT EXISTS zones_management_roles
ON public.zones
FOR ALL
TO authenticated
USING (
  event_id IN (
    SELECT id FROM public.inventory_events WHERE company_id = public.get_auth_company_id()
  )
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
)
WITH CHECK (
  NEW.event_id IN (
    SELECT id FROM public.inventory_events WHERE company_id = public.get_auth_company_id()
  )
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
);


-- 7.10 inventory_items

CREATE POLICY IF NOT EXISTS items_insert_counter_auditor_check
ON public.inventory_items
FOR INSERT
TO authenticated
WITH CHECK (
  NEW.user_id = public.get_auth_user_pk_id()
  AND NEW.zone_id IN (
    SELECT z.id FROM public.zones z
    JOIN public.inventory_events e ON e.id = z.event_id
    WHERE e.company_id = public.get_auth_company_id()
  )
  AND public.get_auth_user_role() IN ('counter','auditor')
);

CREATE POLICY IF NOT EXISTS items_select_full_access_roles
ON public.inventory_items
FOR SELECT
TO authenticated
USING (
  zone_id IN (
    SELECT z.id FROM public.zones z
    JOIN public.inventory_events e ON e.id = z.event_id
    WHERE e.company_id = public.get_auth_company_id()
  )
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
);

CREATE POLICY IF NOT EXISTS items_update_full_access_roles
ON public.inventory_items
FOR UPDATE
TO authenticated
USING (
  zone_id IN (
    SELECT z.id FROM public.zones z
    JOIN public.inventory_events e ON e.id = z.event_id
    WHERE e.company_id = public.get_auth_company_id()
  )
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
)
WITH CHECK (
  NEW.zone_id IN (
    SELECT z.id FROM public.zones z
    JOIN public.inventory_events e ON e.id = z.event_id
    WHERE e.company_id = public.get_auth_company_id()
  )
  AND public.get_auth_user_role() IN ('admin','manager','coordinator','auditor')
);


-- 8) RECOMMENDED ADDITIONAL INDEXES (para performance das policies)
-- (idx_inventory_events_company já existe; garantimos index em zones.event_id e users.supabase_auth_id)
CREATE INDEX IF NOT EXISTS idx_zones_event_id ON public.zones(event_id);
-- users.supabase_auth_id já criado acima


-- END OF SCRIPT