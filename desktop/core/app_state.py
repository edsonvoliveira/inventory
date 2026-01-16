# desktop/core/app_state.py

"""
Responsibilities:
- Core module for app state.
- Provide shared application logic.
"""

from dataclasses import dataclass


@dataclass
class AppState:
    is_authenticated: bool = False
    user_id: str | None = None
    email: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None

    def set_session(
        self,
        *,
        user_id: str | None = None,
        email: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        self.is_authenticated = True
        self.user_id = user_id
        self.email = email
        self.access_token = access_token
        self.refresh_token = refresh_token

    def clear_session(self) -> None:
        self.is_authenticated = False
        self.user_id = None
        self.email = None
        self.access_token = None
        self.refresh_token = None
