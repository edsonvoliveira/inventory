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
from mobile.core.sync_service import _get_app_logger, get_scheduler
from mobile.core.theme import THEME, TOUCH
from mobile.utils.ui import toast


def login_content(page: ft.Page, state: AppState):
    auth_service = AuthService()
    email_field = ft.TextField(
        label="Email",
        width=360,
        height=TOUCH["input_height"],
        prefix_icon=ft.Icons.MAIL_OUTLINE,
    )
    password_field = ft.TextField(
        label="Senha",
        width=360,
        height=TOUCH["input_height"],
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )

    def on_login(e):
        app_logger = _get_app_logger()
        email = (email_field.value or "").strip()
        password = (password_field.value or "").strip()
        result = auth_service.authenticate(email, password)
        if result.ok:
            if state.sync_scheduler is None:
                state.sync_scheduler = get_scheduler()
            state.sync_scheduler.start()
            state.set_session(email=email)
            state.profile = {"email": email}
            toast(page, "Login bem-sucedido", success=True)
            app_logger.info("event=ui_login_success email=%s", email)
            page.go(ROUTES["dashboard"])
        else:
            message = "Login invalido! Verifique as credenciais e tente novamente."
            toast(page, message, success=False)
            app_logger.info("event=ui_login_failed email=%s code=%s", email, result.error_code)

    return ft.Column(
        [
            ft.Text(
                "Acesso ao Sistema IMS",
                size=24,
                color=THEME["text_on_dark"] if state.theme == "dark" else THEME["text_on_light"],
            ),
            email_field,
            password_field,
            ft.ElevatedButton(
                "Entrar",
                on_click=on_login,
                height=TOUCH["button_height"],
                width=360,
                bgcolor=THEME["primary"],
                color="white",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            ),
            ft.TextButton(
                "Esqueceu a Senha?",
                on_click=lambda e: toast(page, "Funcionalidade a implementar!", success=False),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
