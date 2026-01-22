# mobile/main.py

"""
Responsibilities:
- Mobile application entry point.
- Initialize app state and services.
- Set up the main UI layout.
- Handle routing and authentication.
- Start the Flet application.
"""

#mobile/main.py

import flet as ft
import atexit
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from mobile.core.app_state import AppState
from mobile.core.navigation import ROUTES
from mobile.core.theme import THEME, TOUCH
from mobile.core.sync_service import _get_app_logger
from mobile.data.queries import get_local_profile, init_db
from mobile.data.db.connection import get_connection
from mobile.data.repositories.app_meta_repo import get_meta
from mobile.utils.ui import toast
from mobile.views.counting.counting_view import counting_page_content
from mobile.views.dashboard.dashboard_view import dashboard_content
from mobile.views.inventory.inventory_view import inventory_content
from mobile.views.login_view import login_content
from mobile.views.profile_view import profile_content
from mobile.views.settings.settings_view import settings_content
from mobile.views.zone_details_view import zone_details_content

def _suppress_executor_shutdown(loop, context):
    exc = context.get("exception")
    if isinstance(exc, RuntimeError) and "cannot schedule new futures after shutdown" in str(exc):
        return
    loop.default_exception_handler(context)


class _AppEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def new_event_loop(self):
        loop = super().new_event_loop()
        loop.set_exception_handler(_suppress_executor_shutdown)
        return loop


asyncio.set_event_loop_policy(_AppEventLoopPolicy())

STATE = AppState()

REPO_ROOT = Path(__file__).resolve().parents[1]
MOBILE_ENV = REPO_ROOT / "mobile" / ".env"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
if MOBILE_ENV.exists():
    load_dotenv(MOBILE_ENV)
elif BACKEND_ENV.exists():
    load_dotenv(BACKEND_ENV)


def apply_theme(page: ft.Page) -> None:
    if STATE.theme == "dark":
        page.bgcolor = THEME["bg_dark"]
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.bgcolor = THEME["bg_light"]
        page.theme_mode = ft.ThemeMode.LIGHT
    page.update()


def toggle_theme(page: ft.Page) -> None:
    STATE.theme = "light" if STATE.theme == "dark" else "dark"
    apply_theme(page)


class ScreenFactory:
    """Gerencia telas sem blink, com AppBar/Footer fixos."""

    def __init__(self, page: ft.Page, show_footer: bool = True):
        self.page = page
        self.show_footer = show_footer

        self.appbar = self.build_appbar()
        self.main_container = ft.Column(expand=True)
        self.footer = self.build_footer() if self.show_footer else None

        self.view = ft.View()
        controls = [self.appbar, self.main_container]
        if self.footer:
            controls.append(self.footer)
        self.view.controls.append(ft.SafeArea(ft.Column(controls, expand=True), expand=True))

        self.page.views.clear()
        self.page.views.append(self.view)
        self.registry = {}

    def build_appbar(self):
        text_color = THEME["bar_text_dark"] if STATE.theme == "dark" else THEME["bar_text_light"]
        display_name = None
        user_server_id = get_meta("user_server_id")
        if user_server_id is not None:
            conn = get_connection()
            try:
                row = conn.execute(
                    "SELECT name FROM users_local WHERE server_id = ?",
                    (user_server_id,),
                ).fetchone()
                if row and row[0]:
                    display_name = row[0]
            finally:
                conn.close()
        if not display_name:
            display_name = (
                (STATE.profile or {}).get("name")
                or (STATE.profile or {}).get("username")
                or (STATE.profile or {}).get("email")
                or "U"
            )
        initials = "".join([part[:1].upper() for part in display_name.split()[:2]]).strip() or "U"
        avatar_url = (STATE.profile or {}).get("avatar_url") or ""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            "IMS - Mobile",
                            color=text_color,
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                        padding=ft.padding.only(left=8),
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.BRIGHTNESS_6,
                                icon_color=text_color,
                                on_click=lambda e: toggle_theme(self.page),
                            ),
                            ft.GestureDetector(
                                on_tap=lambda e: self.page.go(ROUTES["profile"]),
                                content=ft.CircleAvatar(
                                    content=ft.Text(initials, color="white"),
                                    bgcolor="black",
                                    foreground_image_src=avatar_url or None,
                                    radius=14,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=56,
            bgcolor=THEME["bar_bg_dark"] if STATE.theme == "dark" else THEME["bar_bg_light"],
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            padding=ft.padding.symmetric(horizontal=12),
        )

    def build_footer(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        ft.Icons.HOME,
                        icon_color=THEME["bar_text_dark"] if STATE.theme == "dark" else THEME["bar_text_light"],
                        on_click=lambda e: self.page.go(ROUTES["dashboard"]),
                    ),
                    ft.IconButton(
                        ft.Icons.INVENTORY_2,
                        icon_color=THEME["bar_text_dark"] if STATE.theme == "dark" else THEME["bar_text_light"],
                        on_click=lambda e: self.page.go(ROUTES["inventory"]),
                    ),
                    ft.IconButton(
                        ft.Icons.SETTINGS,
                        icon_color=THEME["bar_text_dark"] if STATE.theme == "dark" else THEME["bar_text_light"],
                        on_click=lambda e: self.page.go(ROUTES["settings"]),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            height=56,
            bgcolor=THEME["bar_bg_dark"] if STATE.theme == "dark" else THEME["bar_bg_light"],
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
        )

    def register(self, route: str, content_builder):
        self.registry[route] = content_builder

    def show(self, route: str):
        try:
            _get_app_logger().info("event=ui_route_change route=%s", route)
            builder = self.registry.get(route)
            if builder:
                if self.page.overlay:
                    self.page.overlay.clear()
                if getattr(self.page, "dialog", None) is not None:
                    self.page.dialog = None
                self.view.controls.clear()
                self.main_container = ft.Column(expand=True)
                controls = [self.appbar, self.main_container]
                if self.footer:
                    controls.append(self.footer)
                self.view.controls.append(ft.SafeArea(ft.Column(controls, expand=True), expand=True))
                self.appbar.visible = route != ROUTES["login"]
                if self.footer:
                    self.footer.visible = route != ROUTES["login"]
                if STATE.sync_scheduler is not None:
                    if route == ROUTES["dashboard"]:
                        def _refresh_dashboard():
                            if self.page.route == ROUTES["dashboard"]:
                                self.page.go(self.page.route)

                        if hasattr(self.page, "call_from_thread"):
                            STATE.sync_scheduler.set_on_cycle_callback(
                                lambda: self.page.call_from_thread(_refresh_dashboard)
                            )
                        else:
                            STATE.sync_scheduler.set_on_cycle_callback(_refresh_dashboard)
                    else:
                        STATE.sync_scheduler.set_on_cycle_callback(None)
                self.main_container.controls.clear()
                self.main_container.controls.append(builder(self.page))
                self.page.update()
            else:
                self.page.go(ROUTES["login"])
        except Exception:
            _get_app_logger().info("event=ui_error_unexpected route=%s", route)
            toast(self.page, "Erro inesperado. Tente novamente.", success=False)
            self.page.go(ROUTES["login"])


# ----------------------
# Main
# ----------------------

def main(page: ft.Page):
    app_logger = _get_app_logger()
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(_suppress_executor_shutdown)
    except RuntimeError:
        pass
    page.title = "Inventory Mobile"
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = False
    page.window.center()
    init_db()
    STATE.theme = "light"
    STATE.profile = {}
    apply_theme(page)

    factory = ScreenFactory(page)
    factory.register(ROUTES["login"], lambda p: login_content(p, STATE))
    factory.register(ROUTES["dashboard"], lambda p: dashboard_content(p, STATE))
    factory.register(ROUTES["inventory"], lambda p: inventory_content(p, STATE))
    factory.register(ROUTES["profile"], lambda p: profile_content(p, STATE))
    factory.register(ROUTES["settings"], lambda p: settings_content(p))
    factory.register(ROUTES["zone_details"], lambda p: zone_details_content(p, STATE))
    factory.register(ROUTES["counting"], lambda p: counting_page_content(p, STATE))

    page.on_route_change = lambda e: factory.show(e.route)
    def _cleanup(e=None):
        app_logger.info("event=app_shutdown_cleanup")
        if STATE.sync_scheduler is not None:
            STATE.sync_scheduler.stop()
            STATE.sync_scheduler = None

    page.on_disconnect = _cleanup
    page.on_window_event = _cleanup
    atexit.register(_cleanup)

    page.go(ROUTES["login"])

    page.update()


if __name__ == "__main__":
    if "THEME" not in locals():
        THEME = {
            "bg_dark": "#1f2226",
            "bg_light": "#f0f0f0",
            "text_on_dark": "#ffffff",
            "text_on_light": "#000000",
            "text_secondary": "#aaa",
            "primary": "#3399FF",
            "success": "#4CAF50",
            "danger": "#F44336",
        }
    if "TOUCH" not in locals():
        TOUCH = {"input_height": 48, "button_height": 50}

    ft.app(target=main, view=ft.AppView.FLET_APP)
