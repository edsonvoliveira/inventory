# mobile/core/app_state.py

"""
Responsibilities:
- Core module for app state.
- Provide shared application logic.
"""

from dataclasses import dataclass, field


@dataclass
class AppState:
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
