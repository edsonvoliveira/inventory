import flet as ft

from desktop.core.app_state import AppState
from desktop.core.layout import AppLayout
from desktop.views.auth.login_view import LoginView
from desktop.views.router import render_page


class AppRouter:
    def __init__(self, page: ft.Page, app_state: AppState, layout: AppLayout, login_view: LoginView):
        self.page = page
        self.app_state = app_state
        self.layout = layout
        self.login_view = login_view
        self.main_view = ft.View("/", controls=[self.layout.main_layout])

    def renderizar_pagina(self, rota):
        return render_page(rota, self.page, self.on_route_change)

    def on_route_change(self, e):
        # 1. LÓGICA DE PROTEÇÃO DE ROTA
        # Se NÃO ESTIVER LOGADO E a rota não for /login, força o login
        if not self.app_state.is_authenticated and self.page.route != "/login":
            self.page.go("/login")
            return

        # 2. ROTA DE LOGIN (Exibir View de Login)
        if self.page.route == "/login":
            self.page.views.clear()
            self.login_view.apply_theme(self.layout.tokens)
            self.page.views.append(self.login_view)
            self.page.update()
            return

        # 3. ROTA DE APLICATIVO PRINCIPAL (Reutiliza View existente)
        self.layout.set_route(self.page.route)

        if self.main_view not in self.page.views:
            self.page.views.clear()
            self.page.views.append(self.main_view)

        # 4. ATUALIZAR CONTEÚDO (sem page.update() aqui)
        nova_coluna = self.renderizar_pagina(self.page.route)
        self.layout.set_content(nova_coluna)

        # Uma única chamada de update no final
        self.page.update()
