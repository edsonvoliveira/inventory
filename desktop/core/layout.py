# desktop/core/layout.py

"""
Responsibilities:
- Core module for layout.
- Provide shared application logic.
"""

import flet as ft

from desktop.core.navigation import NAV_ITEMS
from desktop.core.session_service import SessionService
from desktop.core.theme import build_theme, get_theme_tokens
from desktop.data.db.connection import get_connection
from desktop.widgets.side_menu import SideMenu
from desktop.widgets.top_bar import TopBar


class AppLayout:
    def __init__(self, page: ft.Page, on_toggle_theme, on_navigate, on_logout):
        self.page = page
        self.menu_expandido = True
        self.rota_atual = "/"

        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.tokens = get_theme_tokens(self.page.theme_mode)
        self.page.theme = build_theme(self.tokens)

        self.conteudo = ft.Container(
            expand=True,
            padding=20,
            content=ft.Column(expand=True, spacing=10),
        )

        self.side_menu = SideMenu(NAV_ITEMS, on_navigate, self._alternar_menu, self.tokens)
        self.top_bar = TopBar(
            on_help=lambda e: print("Abrir ajuda"),
            on_toggle_theme=on_toggle_theme,
            on_notifications=lambda e: print("Notificacoes clicadas"),
            on_logout=on_logout,
            on_navigate=on_navigate,
            tokens=self.tokens,
        )

        self.main_layout = ft.Column(
            [
                self.top_bar.container,
                ft.Row(
                    [self.side_menu.container, self.conteudo],
                    expand=True,
                ),
            ],
            expand=True,
        )

        self.aplicar_tema()
        self.atualizar_menu()

    def _alternar_menu(self, e):
        self.menu_expandido = not self.menu_expandido
        self.atualizar_menu()

    def atualizar_menu(self):
        self.side_menu.update(self.menu_expandido, self.rota_atual)
        self.page.update()

    def aplicar_tema(self):
        if self.page.theme_mode not in (ft.ThemeMode.LIGHT, ft.ThemeMode.DARK):
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.tokens = get_theme_tokens(self.page.theme_mode)
        self.page.theme = build_theme(self.tokens)
        self.page.theme.color_scheme = ft.ColorScheme(
            primary=self.tokens.primary,
            secondary=self.tokens.accent,
            error=self.tokens.danger,
        )
        self.page.bgcolor = self.tokens.bg
        self.conteudo.bgcolor = self.tokens.bg
        self.top_bar.set_tokens(self.tokens)
        self.side_menu.set_tokens(self.tokens)
        self.atualizar_menu()

    def refresh_user_initials(self) -> None:
        user_server_id = SessionService.get_user_server_id()
        initials = "??"
        if user_server_id is not None:
            conn = get_connection()
            try:
                row = conn.execute(
                    "SELECT name, email FROM users_local WHERE server_id = ?",
                    (user_server_id,),
                ).fetchone()
            finally:
                conn.close()
            if row:
                name, email = row
                initials = _build_initials(name, email)
        self.top_bar.set_user_initials(initials)
        self.page.update()

    def set_route(self, rota: str):
        self.rota_atual = rota
        self.atualizar_menu()

    def set_content(self, content: ft.Control):
        if isinstance(self.conteudo.content, ft.Column):
            self.conteudo.content.controls.clear()
            if isinstance(content, ft.Column):
                self.conteudo.content.controls.extend(content.controls)
            else:
                self.conteudo.content.controls.append(content)


def _build_initials(name: str | None, email: str | None) -> str:
    raw = (name or "").strip()
    if raw:
        parts = [p for p in raw.replace(".", " ").split() if p]
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()
    if email:
        handle = email.split("@", 1)[0].strip()
        return handle[:2].upper() if handle else "??"
    return "??"

