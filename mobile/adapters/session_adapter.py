from __future__ import annotations

from typing import Optional

from app_core.ports.session_port import SessionPort
from mobile.data.repositories.app_meta_repo import get_meta, set_meta


class MobileSessionAdapter(SessionPort):
    def get_jwt_token(self) -> Optional[str]:
        return get_meta("jwt_token")

    def set_jwt_token(self, token: str) -> None:
        set_meta("jwt_token", token)

    def get_company_server_id(self) -> Optional[str]:
        return get_meta("company_server_id")

    def set_company_server_id(self, company_id: str) -> None:
        set_meta("company_server_id", company_id)

    def get_user_server_id(self) -> Optional[str]:
        return get_meta("user_server_id")

    def set_user_server_id(self, user_id: str) -> None:
        set_meta("user_server_id", user_id)
