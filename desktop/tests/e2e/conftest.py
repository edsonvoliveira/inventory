# desktop/tests/e2e/conftest.py

"""
Responsibilities:
- Define pytest fixtures for this test scope.
- Configure test environment setup and teardown.
"""

# desktop/tests/e2e/conftest.py

import os
import sqlite3
from dataclasses import dataclass

import pytest

from desktop.core.session_service import SessionService
from desktop.core.db_lifecycle import recreate_database
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import set_meta
from typing import Iterator


@dataclass(frozen=True)
class E2EContext:
    """
    Contexto compartilhado para testes E2E.
    Ajuste os valores via variáveis de ambiente para rodar em diferentes ambientes.
    """
    dv_base_url: str
    jwt_token: str
    company_server_id: int


def _env(name: str, default: str) -> str:
    val = os.getenv(name)
    return val if val is not None and val.strip() else default


@pytest.fixture(scope="session")
def e2e_context() -> E2EContext:
    """
    Configuração base do ambiente E2E.
    Você pode configurar via variáveis de ambiente:

    - DV_SERVER_BASE_URL: ex "http://127.0.0.1:8000"
    - E2E_JWT_TOKEN: JWT válido no DV Server (empresa conhecida)
    - E2E_COMPANY_SERVER_ID: company_server_id da empresa do token
    """
    dv_base_url = _env("DV_SERVER_BASE_URL", "http://127.0.0.1:8000")
    jwt_token = _env("E2E_JWT_TOKEN", "")
    company_server_id = int(_env("E2E_COMPANY_SERVER_ID", "1"))

    if not jwt_token:
        raise RuntimeError(
            "E2E_JWT_TOKEN não definido. "
            "Para rodar E2E você precisa fornecer um JWT válido do Supabase/DV Server."
        )

    return E2EContext(
        dv_base_url=dv_base_url.rstrip("/"),
        jwt_token=jwt_token,
        company_server_id=company_server_id,
    )


@pytest.fixture()
def e2e_clean_db(e2e_context: E2EContext) -> Iterator[sqlite3.Connection]:
    """
    Garante um DB local limpo para cada teste E2E.
    Usa recreate_database() (hard reset) para evitar interferência entre testes.
    """
    # garante que o HTTP client use o DV do ambiente
    os.environ["DV_SERVER_BASE_URL"] = e2e_context.dv_base_url

    # recria DB local
    recreate_database()

    conn = get_connection()
    try:
        # define company_server_id no app_meta para operações locais (create/update/soft_delete)
        set_meta("company_server_id", str(e2e_context.company_server_id), conn)

        # opcional: garantir estado limpo de marcadores
        set_meta("bootstrap_done", "", conn)
        set_meta("last_pull_at", "", conn)

        conn.commit()
        yield conn
    finally:
        conn.close()


@pytest.fixture()
def e2e_session(e2e_context: E2EContext):
    """
    Inicializa a sessão (JWT + company) para o teste.
    Mantém explícito e desacoplado do DB.
    """
    SessionService.set_jwt_token(e2e_context.jwt_token)
    SessionService.set_company_server_id(e2e_context.company_server_id)
    yield
    # teardown defensivo
    SessionService.set_jwt_token("")
    SessionService.set_company_server_id(0)


@pytest.fixture()
def e2e_env(e2e_clean_db: sqlite3.Connection, e2e_session, e2e_context: E2EContext) -> E2EContext:
    """
    Fixture composta: DB limpo + sessão pronta.
    Retorna contexto com as infos do ambiente.
    """
    return e2e_context