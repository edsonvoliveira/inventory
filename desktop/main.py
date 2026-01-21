# desktop/main.py

"""
Responsibilities:
- Main application entry point.
- Initialize app state and services.
- Set up the main UI layout.
- Handle routing and authentication.
- Start the Flet application.
"""

import flet as ft
from pathlib import Path
from dotenv import load_dotenv
from desktop.core.app_state import AppState
from desktop.core.auth_service import AuthService
from desktop.core.layout import AppLayout
from desktop.core.router import AppRouter
from desktop.core.sync_service import get_scheduler
from desktop.core.session_service import SessionService
from desktop.bootstrap.bootstrap import bootstrap_app
from desktop.views.auth.login_view import LoginView

REPO_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ENV = REPO_ROOT / "desktop" / ".env"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
if DESKTOP_ENV.exists():
    load_dotenv(DESKTOP_ENV)
elif BACKEND_ENV.exists():
    load_dotenv(BACKEND_ENV)

bootstrap_app()

# ---------------- MAIN ---------------- #
def main(page: ft.Page):
    app_state = AppState()
    auth_service = AuthService()
    scheduler = get_scheduler()

    page.title = "Inventory"
    page.window.maximized = False
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.center() 

    # ---------------- Funções de Autenticação ---------------- #
    def on_login_success(e):
        scheduler.start()
        page.go("/")

    def on_logout(e):
        app_state.clear_session()
        SessionService.clear_session()
        scheduler.stop()
        # Redireciona para a tela de login
        page.go("/login")

    # ---------------- Funções ---------------- #
    def alternar_tema(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        layout.aplicar_tema()
        page.update()

    def navegar(e):
        page.go(e.control.data)

    # ---------------- Layout Principal ----------------
    layout = AppLayout(page, alternar_tema, navegar, on_logout)
    
    # ---------------- INSTANCIAÇÃO DO LOGIN ----------------
    # Instancia a tela de login, passando a função de sucesso
    login_screen = LoginView(page, auth_service, app_state, on_login_success)

    router = AppRouter(page, app_state, layout, login_screen)
    page.on_route_change = router.on_route_change

    # Inicia com a rota de login
    page.go(page.route or "/login")

if __name__ == "__main__":
    ft.app(target=main)
