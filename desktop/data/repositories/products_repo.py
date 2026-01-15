# desktop/data/repositories/products_repo.py

"""
Responsibilities:
- Repository for products data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig

_PRODUCTS_CFG = RepoConfig(
    table="products_local",
    entity_name="products",

    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    active_col="is_active",
    source_col="source",

    enable_outbox=True,

    server_upsert_cols=(
        "uuid",
        "server_id",
        "company_server_id",
        "category_server_id",
        "sku",
        "name",
        "description",
        "uom_base",
        "uom_inventory",
        "conversion_factor",
        "system_qty",
        "cost_price",
        "is_sensitive",
        "serial_number_enabled",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
        "synced",
        "synced_at",
        "source",
    ),

    ui_writable_cols=(
        "category_server_id",
        "sku",
        "name",
        "description",
        "uom_base",
        "uom_inventory",
        "conversion_factor",
        "cost_price",
        "is_sensitive",
        "serial_number_enabled",
        "is_active",
    ),
)

class ProductsRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_PRODUCTS_CFG, conn)