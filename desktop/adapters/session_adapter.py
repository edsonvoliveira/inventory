from __future__ import annotations

from typing import Optional

from app_core.ports.session_port import SessionPort
from desktop.core.session_service import SessionService


class DesktopSessionAdapter(SessionPort):
    def get_jwt_token(self) -> Optional[str]:
        return SessionService.get_jwt_token()

    def set_jwt_token(self, token: str) -> None:
        SessionService.set_jwt_token(token)

    def get_company_server_id(self) -> Optional[str]:
        value = SessionService.get_company_server_id()
        return str(value) if value is not None else None

    def set_company_server_id(self, company_id: str) -> None:
        SessionService.set_company_server_id(int(company_id))

    def get_user_server_id(self) -> Optional[str]:
        value = SessionService.get_user_server_id()
        return str(value) if value is not None else None

    def set_user_server_id(self, user_id: str) -> None:
        SessionService.set_user_server_id(int(user_id))
