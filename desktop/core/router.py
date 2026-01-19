# desktop/core/router.py

"""
Responsibilities:
- Core module for router.
- Provide shared application logic.
"""

import flet as ft

from desktop.core.app_state import AppState
from desktop.core.layout import AppLayout
from desktop.core.navigation import NAV_ITEMS
from desktop.views.auth.login_view import LoginView


class AppRouter:
    def __init__(self, page: ft.Page, app_state: AppState, layout: AppLayout, login_view: LoginView):
        self.page = page
        self.app_state = app_state
        self.layout = layout
        self.login_view = login_view
        self.main_view = ft.View("/", controls=[self.layout.main_layout])
        self._route_map = {item["rota"]: item for item in NAV_ITEMS}

    def _get_entry(self, rota: str):
        return self._route_map.get(rota)

    def renderizar_pagina(self, rota: str):
        entry = self._get_entry(rota)
        if not entry:
            return ft.Column(expand=True, spacing=10)
        factory = entry.get("factory")
        if not factory:
            return ft.Column(expand=True, spacing=10)
        return factory(self.page, self.on_route_change)

    def on_route_change(self, e):
        try:
            route = self.page.route or "/"
            entry = self._get_entry(route)

            # Route protection
            if entry and entry.get("protected") and not self.app_state.is_authenticated and route != "/login":
                self.page.go("/login")
                return

            # Login route
            if route == "/login":
                self.page.views.clear()
                self.login_view.apply_theme(self.layout.tokens)
                self.page.views.append(self.login_view)
                self.page.update()
                return

            if not entry:
                if not self.app_state.is_authenticated:
                    self.page.go("/login")
                    return
                fallback = NAV_ITEMS[0]["rota"] if NAV_ITEMS else "/login"
                self.page.go(fallback)
                return

            # App main view
            self.layout.set_route(route)

            if self.main_view not in self.page.views:
                self.page.views.clear()
                self.page.views.append(self.main_view)

            # Update content
            nova_coluna = self.renderizar_pagina(route)
            self.layout.set_content(nova_coluna)

            # Single update at end
            self.page.update()
        except Exception:
            self._handle_error()

    def _handle_error(self) -> None:
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Erro inesperado. Tente novamente."),
            bgcolor=ft.Colors.RED_400,
            open=True,
            duration=2000,
        )
        self.page.update()
