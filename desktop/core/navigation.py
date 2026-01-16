# desktop/core/navigation.py

"""
Responsibilities:
- Core module for navigation.
- Provide shared application logic.
"""

import flet as ft

from desktop.core.strings import (
    PAGE_HOME_SUBTITLE,
    PAGE_HOME_TITLE,
    SECTION_CONFIG,
    SECTION_HOME,
    SECTION_LOCATION,
    SECTION_PRODUCT,
    SECTION_ROLE,
    SECTION_USER,
)
from desktop.views.management.location_view import render_location_view
from desktop.views.management.product_view import render_product_view
from desktop.views.management.role_view import render_role_view
from desktop.views.management.user_view import render_user_view
from desktop.views.settings.config_view import render_config_view


def _home_factory(page: ft.Page, on_refresh):
    column = ft.Column(expand=True, spacing=10)
    column.controls.append(ft.Text(PAGE_HOME_TITLE, size=24, weight=ft.FontWeight.BOLD))
    column.controls.append(ft.Text(PAGE_HOME_SUBTITLE, size=18))
    return column


NAV_ITEMS = [
    {"icone": ft.Icons.HOME, "nome": SECTION_HOME, "rota": "/", "protected": True, "factory": _home_factory},
    {
        "icone": ft.Icons.ADMIN_PANEL_SETTINGS,
        "nome": SECTION_ROLE,
        "rota": "/role",
        "protected": True,
        "factory": render_role_view,
    },
    {
        "icone": ft.Icons.PERSON,
        "nome": SECTION_USER,
        "rota": "/user",
        "protected": True,
        "factory": render_user_view,
    },
    {
        "icone": ft.Icons.LOCATION_ON,
        "nome": SECTION_LOCATION,
        "rota": "/location",
        "protected": True,
        "factory": render_location_view,
    },
    {
        "icone": ft.Icons.INVENTORY,
        "nome": SECTION_PRODUCT,
        "rota": "/product",
        "protected": True,
        "factory": render_product_view,
    },
    {
        "icone": ft.Icons.SETTINGS,
        "nome": SECTION_CONFIG,
        "rota": "/config",
        "protected": True,
        "factory": lambda page, on_refresh: render_config_view(),
    },
]
