# mobile/views/profile_view.py

"""
Responsibilities:
- Render the profile view.
- Wire UI events and interactions.
"""

import flet as ft

from mobile.core.app_state import AppState
from mobile.core.navigation import ROUTES
from mobile.core.theme import THEME, TOUCH
from mobile.utils.ui import toast


def profile_content(page: ft.Page, state: AppState):
    prof = state.profile or {}
    user_card = ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON, size=48),
                            ft.Text(prof.get("username", "Demo"), size=20),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=12,
                    ),
                    ft.Text(prof.get("email", "demo@example.com"), size=16, color=THEME["text_secondary"]),
                    ft.Text(f"Perfil: {prof.get('role', 'Usuario')}", size=16, color=THEME["text_secondary"]),
                ],
                spacing=8,
            ),
            padding=12,
        ),
        margin=10,
        elevation=2,
    )
    action_card = ft.Container(
        ft.Column(
            [
                ft.ElevatedButton(
                    "Alterar senha",
                    on_click=lambda e: toast(page, "Alterar senha"),
                    height=TOUCH["button_height"],
                ),
                ft.ElevatedButton(
                    "Sair",
                    on_click=lambda e: page.go(ROUTES["login"]),
                    height=TOUCH["button_height"],
                    bgcolor=THEME["danger"],
                    color="white",
                ),
            ],
            spacing=12,
        ),
        padding=12,
    )

    info_card = ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Text("Sistema de Inventário Mobile", size=16),
                    ft.Text("Versão 1.0.0", size=14, color=THEME["text_secondary"]),
                ],
                spacing=4,
            ),
            padding=12,
        ),
        margin=10,
        elevation=2,
    )

    return ft.Column(
        [user_card, action_card, info_card],
        spacing=12,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
