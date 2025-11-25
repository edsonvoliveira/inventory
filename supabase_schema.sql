-------------------------------------------------------------------
--  SUPABASE SCHEMA FINAL
--  Criado para ser executado diretamente no SQL Editor do Supabase
--  Estrutura otimizada e segura para produção
-------------------------------------------------------------------

BEGIN;

-------------------------------------------------------------------
-- 1. ENUMS
-------------------------------------------------------------------
-- RoleEnum: Papéis de Usuário
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'auditor', 'coordinator', 'counter');
-- EventStatus: Status do Evento de Inventário
CREATE TYPE event_status AS ENUM ('planned', 'open', 'counting', 'closed');

-------------------------------------------------------------------
-- 2. MASTER DATA TABLES
-------------------------------------------------------------------

-- Companies (Tenant)
CREATE TABLE public.companies (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    document VARCHAR(15), -- NIF

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------------------------------

-- Users
CREATE TABLE public.users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(20) NOT NULL, -- Hash
    name VARCHAR(100),
    role user_role DEFAULT 'auditor', -- Usa o ENUM criado acima

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_company ON public.users(company_id);

-------------------------------------------------------------------

-- Locations
CREATE TABLE public.locations (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    name VARCHAR(30) NOT NULL,
    address TEXT,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_locations_company ON public.locations(company_id);

-------------------------------------------------------------------

-- Products
CREATE TABLE public.products (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    sku VARCHAR(30) NOT NULL UNIQUE, -- Código ERP
    barcode VARCHAR(15) UNIQUE, -- Código de Barras (EAN)
    name VARCHAR(80) NOT NULL,
    description TEXT,
    category VARCHAR(20),
    uom VARCHAR(5), -- Unidade de Medida (UN, KG)

    default_location_info VARCHAR(30),
    system_qty NUMERIC(12,2) DEFAULT 0.00, -- Estoque Teórico (Snapshot)
    cost_price NUMERIC(12,2),

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_products_company ON public.products(company_id);
CREATE INDEX idx_products_sku ON public.products(sku);
CREATE INDEX idx_products_barcode ON public.products(barcode);

-------------------------------------------------------------------
-- 3. INVENTORY EVENTS
-------------------------------------------------------------------

CREATE TABLE public.inventory_events (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,

    title VARCHAR(50) NOT NULL,
    status event_status DEFAULT 'planned', -- Usa o ENUM criado acima

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inventory_events_company ON public.inventory_events(company_id);
CREATE INDEX idx_inventory_events_location ON public.inventory_events(location_id);

-------------------------------------------------------------------

-- Zones (divisões do evento)
CREATE TABLE public.zones (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES inventory_events(id) ON DELETE CASCADE,

    name VARCHAR(30) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE, 
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_zones_event ON public.zones(event_id);

-------------------------------------------------------------------
-- 4. INVENTORY ITEMS (Log append-only)
-------------------------------------------------------------------

CREATE TABLE public.inventory_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    zone_id INTEGER NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,

    scanned_code VARCHAR(50) NOT NULL,
    qty_counted NUMERIC(12,3) NOT NULL,

    is_new_product BOOLEAN DEFAULT FALSE,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE, -- Para permitir "exclusão lógica" se necessário

    device_timestamp TIMESTAMPTZ NOT NULL, -- Quando foi bipado
    server_timestamp TIMESTAMPTZ DEFAULT NOW() -- Quando chegou no servidor
);

CREATE INDEX idx_items_zone ON public.inventory_items(zone_id);
CREATE INDEX idx_items_product ON public.inventory_items(product_id);
CREATE INDEX idx_items_user ON public.inventory_items(user_id);
CREATE INDEX idx_items_scanned_code ON public.inventory_items(scanned_code);

-------------------------------------------------------------------
-- 5. TRIGGER TO UPDATE updated_at AUTOMATICALLY
-------------------------------------------------------------------

-- Trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger automatically to all tables that have updated_at
DO $$
DECLARE 
    t_name TEXT;
BEGIN
    FOR t_name IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
          AND column_name = 'updated_at'
    LOOP
        EXECUTE format('
            CREATE TRIGGER trg_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE PROCEDURE update_updated_at_column();
        ', t_name, t_name);
    END LOOP;
END;
$$;

-------------------------------------------------------------------
-- END OF SCHEMA
-------------------------------------------------------------------

COMMIT;