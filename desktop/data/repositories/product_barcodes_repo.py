# desktop/data/repositories/product_barcodes_repo.py

"""
Responsibilities:
- Repository for product barcodes data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig


_PRODUCT_BARCODES_CFG = RepoConfig(
    table="product_barcodes_local",
    entity_name="product_barcodes",

    uuid_col="uuid",

    # colunas de controle
    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    source_col="source",
    active_col="is_active",

    enable_outbox=True,

    # campos que a UI pode escrever
    ui_writable_cols=(
        "product_server_id",
        "barcode",
        "description",
    ),

    # colunas usadas no pull (server → local)
    server_upsert_cols=(
        "uuid",
        "server_id",
        "company_server_id",
        "product_server_id",
        "barcode",
        "description",
        "is_active",
        "created_at",
        "updated_at",
        "synced",
        "synced_at",
        "source",
    ),
)


class ProductBarcodesRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_PRODUCT_BARCODES_CFG, conn)
