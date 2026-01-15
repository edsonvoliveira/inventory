# mobile/utils/ui.py

"""
Responsibilities:
- Utility helpers for ui.
- Provide shared helper functions.
"""

import flet as ft

from mobile.core.theme import THEME


def toast(page: ft.Page, text: str, success: bool = True) -> None:
    color = THEME["success"] if success else THEME["danger"]
    snack = ft.SnackBar(content=ft.Text(text), bgcolor=color, open=True, duration=2000)
    page.overlay.append(snack)
    page.update()


def get_option_label(dropdown: ft.Dropdown) -> str:
    selected_key = dropdown.value
    if selected_key is None:
        return "N/A"
    for opt in dropdown.options:  # type: ignore[attr-defined]
        if getattr(opt, "key", None) == selected_key:
            return getattr(opt, "text", "N/A")
    return "N/A"
