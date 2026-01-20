-- SUPABASE SCHEMA PATCH (V9.5)
-- Aplicar em ambiente existente (V9)

-- required_counts >= 1
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'chk_inventory_events_required_counts'
  ) THEN
    ALTER TABLE public.inventory_events
      ADD CONSTRAINT chk_inventory_events_required_counts
      CHECK (required_counts >= 1);
  END IF;
END$$;

-- indices para pull incremental (company_id + updated_at)
CREATE INDEX IF NOT EXISTS idx_companies_company_updated_at
  ON public.companies (id, updated_at);
CREATE INDEX IF NOT EXISTS idx_users_company_updated_at
  ON public.users (company_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_locations_company_updated_at
  ON public.locations (company_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_product_categories_company_updated_at
  ON public.product_categories (company_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_products_company_updated_at
  ON public.products (company_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_product_barcodes_company_updated_at
  ON public.product_barcodes (company_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_inventory_events_company_updated_at
  ON public.inventory_events (company_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_inventory_event_targets_company_updated_at
  ON public.inventory_event_targets (company_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_divergence_reason_company_updated_at
  ON public.divergence_reason_types (company_id, updated_at);

-- append-only: bloquear UPDATE/DELETE nas tabelas de auditoria
CREATE OR REPLACE FUNCTION public.block_update_delete()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'append-only table: %', TG_TABLE_NAME;
END;
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_item_events_no_update_delete'
  ) THEN
    CREATE TRIGGER trg_item_events_no_update_delete
    BEFORE UPDATE OR DELETE ON public.inventory_item_events
    FOR EACH ROW EXECUTE PROCEDURE public.block_update_delete();
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_item_revisions_no_update_delete'
  ) THEN
    CREATE TRIGGER trg_item_revisions_no_update_delete
    BEFORE UPDATE OR DELETE ON public.inventory_item_revisions
    FOR EACH ROW EXECUTE PROCEDURE public.block_update_delete();
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_workflow_logs_no_update_delete'
  ) THEN
    CREATE TRIGGER trg_workflow_logs_no_update_delete
    BEFORE UPDATE OR DELETE ON public.workflow_logs
    FOR EACH ROW EXECUTE PROCEDURE public.block_update_delete();
  END IF;
END$$;

-- status finalized: bloquear writes relacionadas
CREATE OR REPLACE FUNCTION public.block_when_event_finalized()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  v_event_id BIGINT;
  v_status public.event_status;
BEGIN
  IF TG_TABLE_NAME = 'inventory_events' THEN
    RETURN NEW;
  END IF;

  IF TG_TABLE_NAME = 'zones' THEN
    v_event_id := COALESCE(NEW.event_id, OLD.event_id);
  ELSIF TG_TABLE_NAME = 'inventory_event_targets' THEN
    v_event_id := COALESCE(NEW.event_id, OLD.event_id);
  ELSIF TG_TABLE_NAME = 'inventory_items' THEN
    SELECT z.event_id INTO v_event_id
    FROM public.zones z
    WHERE z.id = COALESCE(NEW.zone_id, OLD.zone_id);
  ELSIF TG_TABLE_NAME = 'zone_user_progress' THEN
    SELECT z.event_id INTO v_event_id
    FROM public.zones z
    WHERE z.id = COALESCE(NEW.zone_id, OLD.zone_id);
  END IF;

  IF v_event_id IS NOT NULL THEN
    SELECT status INTO v_status FROM public.inventory_events WHERE id = v_event_id;
    IF v_status = 'finalized' THEN
      RAISE EXCEPTION 'event finalized: writes blocked';
    END IF;
  END IF;

  RETURN NEW;
END;
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_zones_block_finalized'
  ) THEN
    CREATE TRIGGER trg_zones_block_finalized
    BEFORE INSERT OR UPDATE OR DELETE ON public.zones
    FOR EACH ROW EXECUTE PROCEDURE public.block_when_event_finalized();
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_targets_block_finalized'
  ) THEN
    CREATE TRIGGER trg_targets_block_finalized
    BEFORE INSERT OR UPDATE OR DELETE ON public.inventory_event_targets
    FOR EACH ROW EXECUTE PROCEDURE public.block_when_event_finalized();
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_items_block_finalized'
  ) THEN
    CREATE TRIGGER trg_items_block_finalized
    BEFORE INSERT OR UPDATE OR DELETE ON public.inventory_items
    FOR EACH ROW EXECUTE PROCEDURE public.block_when_event_finalized();
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_progress_block_finalized'
  ) THEN
    CREATE TRIGGER trg_progress_block_finalized
    BEFORE INSERT OR UPDATE OR DELETE ON public.zone_user_progress
    FOR EACH ROW EXECUTE PROCEDURE public.block_when_event_finalized();
  END IF;
END$$;
