# desktop/utils/notifications.py

"""
Responsibilities:
- Shared UI notifications.
"""

import flet as ft


def show_auto_refresh(page: ft.Page) -> None:
    page.snack_bar = ft.SnackBar(
        content=ft.Text("Dados atualizados automaticamente."),
        bgcolor=ft.Colors.GREEN_200,
        open=True,
        duration=1500,
    )
    page.update()
