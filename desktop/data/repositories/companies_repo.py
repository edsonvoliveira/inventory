# desktop/data/repositories/companies_repo.py

"""
Responsibilities:
- Repository for companies data.
- Define persistence and sync behavior.
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig

_COMPANIES_CFG = RepoConfig(
    table="companies_local",
    entity_name="companies",

    uuid_col="uuid",

    # controle
    synced_col="synced",
    synced_at_col="synced_at",
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    source_col="source",
    active_col="is_active",

    enable_outbox=False,   # regra de domínio

    # UI NÃO cria empresa offline; apenas leitura
    ui_writable_cols=(),

    # pull / bootstrap
    server_upsert_cols=(
        "uuid",
        "server_id",
        "name",
        "vat_number",
        "country_code",
        "address",
        "is_active",
        "created_at",
        "updated_at",
        "synced",
        "synced_at",
        "source",
    ),
)

class CompaniesRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_COMPANIES_CFG, conn)
