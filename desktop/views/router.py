# desktop/views/router.py

"""
Responsibilities:
- Module responsibilities not classified.
"""

import flet as ft

from desktop.core.strings import PAGE_HOME_SUBTITLE, PAGE_HOME_TITLE
from desktop.views.management.company_view import render_company_view
from desktop.views.management.location_view import render_location_view
from desktop.views.management.product_view import render_product_view
from desktop.views.management.role_view import render_role_view
from desktop.views.management.user_view import render_user_view
from desktop.views.settings.config_view import render_config_view


def render_page(rota: str, page: ft.Page, on_refresh):
    if rota == "/":
        coluna = ft.Column(expand=True, spacing=10)
        coluna.controls.append(ft.Text(PAGE_HOME_TITLE, size=24, weight=ft.FontWeight.BOLD))
        coluna.controls.append(ft.Text(PAGE_HOME_SUBTITLE, size=18))
        return coluna
    if rota == "/company":
        return render_company_view(page, on_refresh)
    if rota == "/role":
        return render_role_view(page, on_refresh)
    if rota == "/user":
        return render_user_view(page, on_refresh)
    if rota == "/location":
        return render_location_view(page, on_refresh)
    if rota == "/product":
        return render_product_view(page, on_refresh)
    if rota == "/config":
        return render_config_view(page, on_refresh)
    return ft.Column(expand=True, spacing=10)
