-- ESTE SCRIPT CRIA TODAS AS TABELAS NO SEU BANCO DE DADOS CENTRAL (POSTGRESQL)

-- 1. CRIAÇÃO DOS ENUMERADORES (Tipos de Dados Customizados)
--------------------------------------------------------------
-- RoleEnum: Papéis de Usuário
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'auditor');

-- EventStatus: Status do Evento de Inventário
CREATE TYPE event_status AS ENUM ('planned', 'open', 'counting', 'closed');

-- 2. CRIAÇÃO DAS TABELAS DE DADOS MESTRE
--------------------------------------------------------------

-- Tabela Companies (Empresas - Tenant)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    document VARCHAR(50), -- CNPJ/NIF
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- Otimizado para Sync
);

-- Tabela Users (Usuários)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- Hash
    name VARCHAR(255),
    role user_role DEFAULT 'auditor', -- Usa o ENUM criado acima
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela Locations (Locais Físicos)
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    
    name VARCHAR(255) NOT NULL,
    address TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela Products (Catálogo Mestre)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    
    sku VARCHAR(100) UNIQUE NOT NULL,      -- Código ERP
    barcode VARCHAR(100) UNIQUE,           -- Código de Barras (EAN)
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    uom VARCHAR(50),                       -- Unidade de Medida (UN, KG)
    
    default_location_info VARCHAR(255),
    system_qty REAL DEFAULT 0.0,           -- Estoque Teórico (Snapshot)
    cost_price REAL,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela InventoryEvents (Eventos de Balanço)
CREATE TABLE inventory_events (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    location_id INTEGER REFERENCES locations(id),
    
    title VARCHAR(255) NOT NULL,
    status event_status DEFAULT 'planned', -- Usa o ENUM criado acima
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela Zones (Divisões de um Evento)
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES inventory_events(id),
    
    name VARCHAR(255) NOT NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela InventoryItems (Log de Auditoria / Contagem - Append-Only)
-- Esta tabela não precisa de 'updated_at', pois logs são imutáveis
CREATE TABLE inventory_items (
    id BIGSERIAL PRIMARY KEY,
    
    zone_id INTEGER REFERENCES zones(id),
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    
    scanned_code VARCHAR(100) NOT NULL,
    qty_counted REAL NOT NULL,
    
    is_new_product BOOLEAN DEFAULT FALSE,
    notes TEXT,

    is_active BOOLEAN DEFAULT TRUE, -- Para anular o registro de contagem
    
    device_timestamp TIMESTAMP WITH TIME ZONE NOT NULL, -- Quando foi bipado
    server_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- Quando chegou no servidor
);

-- 3. CRIAÇÃO DOS TRIGGERS DE ATUALIZAÇÃO (CRÍTICO PARA SYNC)
-------------------------------------------------------------------------
-- O PostgreSQL não atualiza automaticamente a data. Precisamos de um TRIGGER.
-- O Sync Engine confia que updated_at é a hora da última alteração.

-- Função genérica para atualizar a coluna 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplica o Trigger em todas as tabelas replicadas
DO $$
DECLARE
    t_name text;
BEGIN
    FOR t_name IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name IN ('companies', 'users', 'locations', 'products', 'inventory_events', 'zones') 
    LOOP
        EXECUTE format('
            CREATE TRIGGER set_updated_at_timestamp 
            BEFORE UPDATE ON %I 
            FOR EACH ROW 
            EXECUTE PROCEDURE update_updated_at_column();
        ', t_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;