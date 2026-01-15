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
