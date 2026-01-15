# desktop/core/session_service.py

"""
Responsibilities:
- Service layer for session workflows.
- Coordinate related operations and dependencies.
"""

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
    REFRESH_TOKEN_KEY = "refresh_token"
    EXPIRES_AT_KEY = "expires_at"
    EXPIRES_IN_KEY = "expires_in"
    COMPANY_SERVER_ID_KEY = "company_server_id"
    USER_SERVER_ID_KEY = "user_server_id"

    @classmethod
    def set_jwt_token(cls, token: str) -> None:
        conn = get_connection()
        try:
            set_meta(cls.JWT_KEY, token, conn)
        finally:
            conn.close()

    @classmethod
    def get_jwt_token(cls) -> Optional[str]:
        conn = get_connection()
        try:
            return get_meta(cls.JWT_KEY, conn)
        finally:
            conn.close()

    @classmethod
    def clear_session(cls) -> None:
        conn = get_connection()
        try:
            set_meta(cls.JWT_KEY, "", conn)
            set_meta(cls.REFRESH_TOKEN_KEY, "", conn)
            set_meta(cls.EXPIRES_AT_KEY, "", conn)
            set_meta(cls.EXPIRES_IN_KEY, "", conn)
            set_meta(cls.COMPANY_SERVER_ID_KEY, "", conn)
            set_meta(cls.USER_SERVER_ID_KEY, "", conn)
        finally:
            conn.close()

    @classmethod
    def set_auth_tokens(
        cls,
        access_token: str,
        refresh_token: str,
        expires_in: int | None,
        expires_at: int | None,
    ) -> None:
        conn = get_connection()
        try:
            set_meta(cls.JWT_KEY, access_token, conn)
            set_meta(cls.REFRESH_TOKEN_KEY, refresh_token, conn)
            if expires_in is not None:
                set_meta(cls.EXPIRES_IN_KEY, str(expires_in), conn)
            if expires_at is not None:
                set_meta(cls.EXPIRES_AT_KEY, str(expires_at), conn)
        finally:
            conn.close()

    @classmethod
    def get_refresh_token(cls) -> Optional[str]:
        conn = get_connection()
        try:
            return get_meta(cls.REFRESH_TOKEN_KEY, conn)
        finally:
            conn.close()

    @classmethod
    def get_expires_at(cls) -> Optional[int]:
        conn = get_connection()
        try:
            value = get_meta(cls.EXPIRES_AT_KEY, conn)
            return int(value) if value and value.isdigit() else None
        finally:
            conn.close()

    @classmethod
    def set_company_server_id(cls, company_server_id: int) -> None:
        conn = get_connection()
        try:
            set_meta(cls.COMPANY_SERVER_ID_KEY, str(company_server_id), conn)
        finally:
            conn.close()

    @classmethod
    def get_company_server_id(cls) -> Optional[int]:
        conn = get_connection()
        try:
            value = get_meta(cls.COMPANY_SERVER_ID_KEY, conn)
            return int(value) if value else None
        finally:
            conn.close()

    @classmethod
    def set_user_server_id(cls, user_server_id: int) -> None:
        conn = get_connection()
        try:
            set_meta(cls.USER_SERVER_ID_KEY, str(user_server_id), conn)
        finally:
            conn.close()

    @classmethod
    def get_user_server_id(cls) -> Optional[int]:
        conn = get_connection()
        try:
            value = get_meta(cls.USER_SERVER_ID_KEY, conn)
            return int(value) if value else None
        finally:
            conn.close()
