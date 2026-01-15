# desktop/views/auth/login_view.py

"""
Responsibilities:
- Render the login view.
- Wire UI events and interactions.
"""

import flet as ft

from desktop.core.app_state import AppState
from desktop.core.auth_service import AuthService
from desktop.core.strings import (
    LOGIN_BUTTON,
    LOGIN_FORGOT,
    LOGIN_INVALID,
    LOGIN_REQUIRED,
    LOGIN_TITLE,
)
from desktop.core.theme import ThemeTokens, get_theme_tokens


class LoginView(ft.View):
    """
    Representa a tela de login do aplicativo.
    
    Recebe uma função de callback que é executada em caso de login bem-sucedido.
    """
    def __init__(self, page: ft.Page, auth_service: AuthService, app_state: AppState, on_login_success):
        super().__init__(
            route="/login",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            padding=50,
        )
        self.page = page
        self.auth_service = auth_service
        self.app_state = app_state
        self.on_login_success = on_login_success
        self.tokens = get_theme_tokens(self.page.theme_mode)
        
        # ---------------- Controles de Formulário ----------------
        self.email_field = ft.TextField(
            label="Email",
            width=300,
            prefix_icon=ft.Icons.MAIL_OUTLINE,
            autofocus=True,
        )
        self.password_field = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            width=300,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
        )
        # Control para exibir mensagens de erro/status
        self.status_message = ft.Text("", color=self.tokens.accent)

        # ---------------- Layout da Tela ----------------
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(LOGIN_TITLE, size=28, weight=ft.FontWeight.BOLD, color=self.tokens.text),
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        self.email_field,
                        self.password_field,
                        self.status_message,  # Adicionado para exibir mensagens de erro
                        ft.ElevatedButton(
                            LOGIN_BUTTON,
                            on_click=self._handle_login,
                            width=300,
                            height=40,
                            icon=ft.Icons.LOGIN,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
                        ),
                        ft.TextButton(LOGIN_FORGOT, on_click=lambda e: print("Acessar recuperação de senha")),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                padding=40,
                border_radius=15,
                width=450,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                ),
                bgcolor=self.tokens.surface,
            )
        ]

    def apply_theme(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.status_message.color = tokens.accent
        # A view usa container único; para manter leveza, apenas atualiza o necessário
        if self.controls and isinstance(self.controls[0], ft.Container):
            self.controls[0].bgcolor = tokens.surface

    def _handle_login(self, e):
        """Lógica de autenticação e redirecionamento."""
        email = (self.email_field.value or "").strip()
        password = (self.password_field.value or "").strip()
        
        # Limpa o texto de erro anterior
        self.status_message.value = ""
        self.page.update()

        # Validação de campos vazios
        if not email or not password:
            self.status_message.value = LOGIN_REQUIRED
            self.page.update()
            return
            
        if self.auth_service.authenticate(email, password):
            self.app_state.is_authenticated = True
            self.on_login_success(e)
        else:
            self.status_message.value = LOGIN_INVALID
            self.password_field.value = ""
            self.page.update()
