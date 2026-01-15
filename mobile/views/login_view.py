# mobile/views/login_view.py

"""
Responsibilities:
- Render the login view.
- Wire UI events and interactions.
"""

import flet as ft

from mobile.core.app_state import AppState
from mobile.core.auth_service import AuthService
from mobile.core.navigation import ROUTES
from mobile.core.sync_service import SyncScheduler
from mobile.core.theme import THEME, TOUCH
from mobile.utils.ui import toast


def login_content(page: ft.Page, state: AppState):
    auth_service = AuthService()
    email_field = ft.TextField(label="Email", width=360, height=TOUCH["input_height"])
    password_field = ft.TextField(
        label="Senha", width=360, height=TOUCH["input_height"], password=True
    )

    def on_login(e):
        email = (email_field.value or "").strip()
        password = (password_field.value or "").strip()
        try:
            auth_service.authenticate(email, password)
            if state.sync_scheduler is None:
                state.sync_scheduler = SyncScheduler()
                state.sync_scheduler.start()
            state.profile = {"email": email}
            toast(page, "Login bem-sucedido", success=True)
            page.go(ROUTES["dashboard"])
        except Exception as ex:
            toast(page, f"Erro no login: {ex}", success=False)

    return ft.Column(
        [
            ft.Text(
                "Entrar",
                size=24,
                color=THEME["text_on_dark"] if state.theme == "dark" else THEME["text_on_light"],
            ),
            email_field,
            password_field,
            ft.ElevatedButton("Entrar", on_click=on_login, height=TOUCH["button_height"]),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
