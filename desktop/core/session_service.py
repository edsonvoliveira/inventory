#desktop/core/session_service.py
"""
Responsabilities:
- Manage user sessions
- Handle login/logout
- Store session data
- Provide session validation
- Support session expiration
"""

from typing import Optional
from desktop.data.repositories.app_meta_repo import get_meta, set_meta
from desktop.data.db.connection import get_connection


class SessionService:
    """
    Gerencia o estado da sessão local (JWT, empresa, usuário).
    Não faz chamadas HTTP.
    """

    JWT_KEY = "jwt_token"
    COMPANY_SERVER_ID_KEY = "company_server_id"
    USER_SERVER_ID_KEY = "user_server_id"

    @classmethod
    def set_jwt_token(cls, token: str) -> None:
        conn = get_connection()
        set_meta(cls.JWT_KEY, token, conn)

    @classmethod
    def get_jwt_token(cls) -> Optional[str]:
        conn = get_connection()
        return get_meta(cls.JWT_KEY, conn)

    @classmethod
    def clear_session(cls) -> None:
        conn = get_connection()
        set_meta(cls.JWT_KEY, "", conn)
        set_meta(cls.COMPANY_SERVER_ID_KEY, "", conn)
        set_meta(cls.USER_SERVER_ID_KEY, "", conn)

    @classmethod
    def set_company_server_id(cls, company_server_id: int) -> None:
        conn = get_connection()
        set_meta(cls.COMPANY_SERVER_ID_KEY, str(company_server_id), conn)

    @classmethod
    def get_company_server_id(cls) -> Optional[int]:
        conn = get_connection()
        value = get_meta(cls.COMPANY_SERVER_ID_KEY, conn)
        return int(value) if value else None

    @classmethod
    def set_user_server_id(cls, user_server_id: int) -> None:
        conn = get_connection()
        set_meta(cls.USER_SERVER_ID_KEY, str(user_server_id), conn)

    @classmethod
    def get_user_server_id(cls) -> Optional[int]:
        conn = get_connection()
        value = get_meta(cls.USER_SERVER_ID_KEY, conn)
        return int(value) if value else None