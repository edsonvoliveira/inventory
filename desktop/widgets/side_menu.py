# desktop/widgets/side_menu.py

"""
Responsibilities:
- Reusable UI widget for side menu.
- Expose UI controls and styling hooks.
"""

import flet as ft

from desktop.core.theme import ThemeTokens


class SideMenu:
    def __init__(self, sections, on_navigate, on_toggle, tokens: ThemeTokens):
        self.sections = sections
        self.on_navigate = on_navigate
        self.on_toggle = on_toggle
        self.tokens = tokens
        self.list_column = ft.Column(expand=True, spacing=2)

        self.menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip="Expandir/retrair menu",
            on_click=self.on_toggle,
            icon_color=self.tokens.menu_text,
        )

        self.container = ft.Container(
            width=220,
            bgcolor=self.tokens.menu_bg,
            content=ft.Column(
                [
                    ft.Container(
                        content=self.menu_button,
                        alignment=ft.alignment.center_left,
                        padding=ft.padding.only(top=10, left=10),
                    ),
                    ft.Divider(),
                    self.list_column,
                ],
                expand=True,
                spacing=0,
            ),
        )

    def _criar_item_menu(self, secao, expanded: bool, current_route: str):
        ativo = current_route == secao["rota"]
        cor_fundo = self.tokens.menu_active_bg if ativo else None
        cor_texto = self.tokens.menu_text if ativo else self.tokens.menu_text_muted
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(secao["icone"], color=cor_texto),
                    ft.Text(secao["nome"], color=cor_texto) if expanded else ft.Container(),
                ],
                alignment=ft.MainAxisAlignment.START if expanded else ft.MainAxisAlignment.CENTER,
                spacing=10 if expanded else 0,
            ),
            padding=10,
            tooltip=secao["nome"],
            on_click=self.on_navigate,
            data=secao["rota"],
            border_radius=ft.border_radius.all(6),
            ink=True,
            bgcolor=cor_fundo,
        )

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.container.bgcolor = tokens.menu_bg
        self.menu_button.icon_color = tokens.menu_text

    def update(self, expanded: bool, current_route: str):
        self.list_column.controls.clear()
        for secao in self.sections:
            if secao.get("hidden"):
                continue
            self.list_column.controls.append(self._criar_item_menu(secao, expanded, current_route))
        self.container.width = 220 if expanded else 80
