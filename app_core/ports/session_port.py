from __future__ import annotations

from typing import Protocol, Optional


class SessionPort(Protocol):
    def get_jwt_token(self) -> Optional[str]:
        ...

    def set_jwt_token(self, token: str) -> None:
        ...

    def get_company_server_id(self) -> Optional[str]:
        ...

    def set_company_server_id(self, company_id: str) -> None:
        ...

    def get_user_server_id(self) -> Optional[str]:
        ...

    def set_user_server_id(self, user_id: str) -> None:
        ...
