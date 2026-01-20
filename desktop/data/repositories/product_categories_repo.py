# desktop/data/repositories/product_categories_repo.py

"""
Responsibilities:
- Repository for product categories data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig


_PRODUCT_CATEGORIES_CFG = RepoConfig(
    table="product_categories_local",
    entity_name="product_categories",

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
        "code",
        "name",
        "description",
        "is_active",
        "created_at",
        "updated_at",
        "synced",
        "synced_at",
        "source",
    ),

    ui_writable_cols=(
        "code",
        "name",
        "description",
        "is_active",
    ),
)


class ProductCategoriesRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_PRODUCT_CATEGORIES_CFG, conn)
