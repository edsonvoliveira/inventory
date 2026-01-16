# desktop/widgets/top_bar.py

"""
Responsibilities:
- Reusable UI widget for top bar.
- Expose UI controls and styling hooks.
"""

import flet as ft

from desktop.core.strings import APP_TITLE
from desktop.core.theme import ThemeTokens


class TopBar:
    def __init__(self, on_help, on_toggle_theme, on_notifications, on_logout, tokens: ThemeTokens):
        self.tokens = tokens

        self.title = ft.Text(
            APP_TITLE,
            size=22,
            weight=ft.FontWeight.BOLD,
            color=tokens.topbar_text,
        )
        self.help_button = ft.IconButton(
            icon=ft.Icons.HELP,
            tooltip="Ajuda",
            on_click=on_help,
            icon_color=tokens.topbar_text,
        )
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Alternar modo claro/escuro",
            on_click=on_toggle_theme,
            icon_color=tokens.topbar_text,
        )
        self.notifications_button = ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS,
            tooltip="Notificações",
            on_click=on_notifications,
            icon_color=tokens.topbar_text,
        )
        self.avatar_text = ft.Text("EO", color=tokens.topbar_text)
        self.avatar = ft.CircleAvatar(
            content=self.avatar_text,
            bgcolor=tokens.primary_dark,
            tooltip="Perfil do usuario",
        )
        self.user_menu = ft.PopupMenuButton(
            content=self.avatar,
            items=[ft.PopupMenuItem(text="Logout", on_click=on_logout)],
        )
        self.container = ft.Container(
            height=60,
            bgcolor=tokens.topbar_bg,
            content=ft.Row(
                [
                    self.title,
                    ft.Row(
                        [
                            self.help_button,
                            self.theme_button,
                            self.notifications_button,
                            self.user_menu,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                spacing=20,
            ),
            padding=ft.padding.symmetric(horizontal=20),
        )

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.container.bgcolor = tokens.topbar_bg
        self.title.color = tokens.topbar_text
        self.help_button.icon_color = tokens.topbar_text
        self.theme_button.icon_color = tokens.topbar_text
        self.notifications_button.icon_color = tokens.topbar_text
        self.avatar_text.color = tokens.topbar_text
        self.avatar.bgcolor = tokens.primary_dark


