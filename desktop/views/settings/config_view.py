import flet as ft

from desktop.core.strings import CONFIG_SUBTITLE, CONFIG_TITLE


def render_config_view():
    coluna = ft.Column(expand=True, spacing=10)
    coluna.controls.append(ft.Text(CONFIG_TITLE, size=24, weight=ft.FontWeight.BOLD))
    coluna.controls.append(ft.Text(CONFIG_SUBTITLE))
    return coluna
