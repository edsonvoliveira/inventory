# mobile/core/app_state.py

"""
Responsibilities:
- Core module for app state.
- Provide shared application logic.
"""

from dataclasses import dataclass, field


@dataclass
class AppState:
    is_authenticated: bool = False
    user_id: str | None = None
    email: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    profile: dict | None = None
    selected_location: int | None = None
    selected_event: int | None = None
    selected_zone: int | None = None
    selected_zone_name: str | None = None
    selected_location_name: str | None = None
    selected_event_name: str | None = None
    scanner: object | None = None
    scanning: bool = False
    theme: str = "dark"
    counted_product_ids_cache: set[int] = field(default_factory=set)
    items_counted: int = 0
    sync_scheduler: object | None = None

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
