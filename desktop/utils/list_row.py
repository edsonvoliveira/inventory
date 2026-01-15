# desktop/utils/list_row.py

"""
Responsibilities:
- Utility helpers for list row.
- Provide shared helper functions.
"""

import flet as ft


def build_list_row(label: str, actions: list[ft.Control]):
    return ft.Row(
        [
            ft.Text(label, expand=1),
            *actions,
        ],
        spacing=10,
    )
