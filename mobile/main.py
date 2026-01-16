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

from mobile.core.app_state import AppState
from mobile.core.navigation import ROUTES
from mobile.core.theme import THEME, TOUCH
from mobile.data.queries import get_local_profile, init_db, seed_minimal_data
from mobile.utils.ui import toast
from mobile.views.counting.counting_view import counting_page_content
from mobile.views.dashboard.dashboard_view import dashboard_content
from mobile.views.login_view import login_content
from mobile.views.profile_view import profile_content
from mobile.views.zone_details_view import zone_details_content

STATE = AppState()


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
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Inventory Mobile",
                        color=THEME["bar_text_dark"] if STATE.theme == "dark" else THEME["bar_text_light"],
                    ),
                    ft.IconButton(
                        ft.Icons.BRIGHTNESS_6,
                        icon_color=THEME["bar_text_dark"] if STATE.theme == "dark" else THEME["bar_text_light"],
                        on_click=lambda e: toggle_theme(self.page),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=56,
            bgcolor=THEME["bar_bg_dark"] if STATE.theme == "dark" else THEME["bar_bg_light"],
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
                        ft.Icons.PERSON,
                        icon_color=THEME["bar_text_dark"] if STATE.theme == "dark" else THEME["bar_text_light"],
                        on_click=lambda e: self.page.go(ROUTES["profile"]),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            height=56,
            bgcolor=THEME["bar_bg_dark"] if STATE.theme == "dark" else THEME["bar_bg_light"],
        )

    def register(self, route: str, content_builder):
        self.registry[route] = content_builder

    def show(self, route: str):
        try:
            builder = self.registry.get(route)
            if builder:
                if self.footer:
                    self.footer.visible = route != ROUTES["login"]
                self.main_container.controls.clear()
                self.main_container.controls.append(builder(self.page))
                self.page.update()
            else:
                self.page.go(ROUTES["login"])
        except Exception:
            toast(self.page, "Erro inesperado. Tente novamente.", success=False)
            self.page.go(ROUTES["login"])


# ----------------------
# Main
# ----------------------

def main(page: ft.Page):
    page.title = "Inventory Mobile"
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = False
    page.window.center()
    init_db()
    seed_minimal_data()
    STATE.profile = {}
    apply_theme(page)

    factory = ScreenFactory(page)
    factory.register(ROUTES["login"], lambda p: login_content(p, STATE))
    factory.register(ROUTES["dashboard"], lambda p: dashboard_content(p, STATE))
    factory.register(ROUTES["profile"], lambda p: profile_content(p, STATE))
    factory.register(ROUTES["zone_details"], lambda p: zone_details_content(p, STATE))
    factory.register(ROUTES["counting"], lambda p: counting_page_content(p, STATE))

    page.on_route_change = lambda e: factory.show(e.route)

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
