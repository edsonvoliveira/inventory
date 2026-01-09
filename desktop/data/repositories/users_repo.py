# desktop/data/repositories/users_repo.py

"""
Responsabilities:
- Repository for users entity
- Inherits basic CRUD, outbox, and sync from BaseRepo
- Configured via RepoConfig for users-specific behavior
- Users do not participate in sync push operations
"""

from desktop.data.repositories.base_repo import BaseRepo, RepoConfig

_USERS_CFG = RepoConfig(
    table="users_local",
    entity_name="users",

    uuid_col="uuid",

    # controle
    synced_col=None,          # não participa de push
    synced_at_col=None,
    updated_at_col="updated_at",
    deleted_at_col="deleted_at",
    source_col="source",
    active_col="is_active",

    enable_outbox=False,      # regra de domínio

    # UI não cria/edita usuários offline
    ui_writable_cols=(),

    # pull / bootstrap (linha completa vinda do servidor)
    server_upsert_cols=(
        "uuid",
        "server_id",
        "email",
        "username",
        "name",
        "role",
        "company_server_id",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
        "source",
    ),
)

class UsersRepo(BaseRepo):
    def __init__(self, conn=None):
        super().__init__(_USERS_CFG, conn)