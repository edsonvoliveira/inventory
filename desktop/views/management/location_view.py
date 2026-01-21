# desktop/views/management/location_view.py

"""
Responsibilities:
- Render the location view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.location_service import LocationService
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    FIELD_NAME,
    HINT_LOCATION_NAME,
    LOCATION_ADD,
    LOCATION_ADD_TITLE,
    LOCATION_EDIT_TITLE,
    LOCATION_TITLE,
)
from desktop.utils.dialogs import action_button, form_column, open_form_dialog
from desktop.utils.event_bus import event_bus


def render_location_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    service = LocationService()
    result = service.list()
    locais = result.data or []

    if not result.ok:
        list_view.controls.append(ft.Text(result.message or "Erro ao carregar locais."))

    def criar_local(e):
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_LOCATION_NAME, autofocus=True)
        theme = page.theme
        error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
        dlg_required_msg = ft.Text("", color=error_color)

        def salvar_local(e, dlg):
            nome = dlg_name.value or ""
            result = service.create(nome)
            if not result.ok:
                if result.error_code == "VALIDATION_ERROR":
                    dlg_required_msg.value = "Informacoes obrigatorias"
                    dlg_name.border_color = error_color
                    dlg_name.focused_border_color = error_color
                    dlg_name.update()
                    dlg_required_msg.update()
                return
            dlg_required_msg.value = ""
            dlg.open = False
            page.update()
            on_refresh(None)
            event_bus.publish("locations_changed")
            event_bus.mark_dirty("/inventory-events")

        open_form_dialog(
            page,
            LOCATION_ADD_TITLE,
            form_column([dlg_name, dlg_required_msg]),
            salvar_local,
            BTN_CREATE,
            width=500,
            height=250,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(LOCATION_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{LOCATION_ADD}  ", icon=ICON_ADD, on_click=criar_local),
            ],
            spacing=5,
        )
    )

    header_bg = getattr(ft.Colors, "BLUE_GREY_50", ft.Colors.GREY_200)
    line_color = getattr(ft.Colors, "BLUE_GREY_100", ft.Colors.GREY_300)

    def _header_cell(label: str, *, width: Optional[int] = None, expand: Optional[int] = None):
        return ft.Container(
            content=ft.Text(label, weight=ft.FontWeight.BOLD, size=12),
            width=width,
            expand=expand,
            padding=ft.padding.symmetric(vertical=8, horizontal=10),
        )

    def _row_cell(value: str, *, width: Optional[int] = None, expand: Optional[int] = None):
        return ft.Container(
            content=ft.Text(value, size=12),
            width=width,
            expand=expand,
            padding=ft.padding.symmetric(vertical=8, horizontal=10),
        )

    def _build_grid_header():
        return ft.Container(
            content=ft.Row(
                [
                    _header_cell("ID", width=60),
                    _header_cell("Nome", expand=3),
                    _header_cell("Acoes", width=120),
                ],
                spacing=0,
            ),
            bgcolor=header_bg,
            border=ft.border.only(
                top=ft.BorderSide(2, line_color),
                bottom=ft.BorderSide(2, line_color),
            ),
        )

    def _build_grid_row(local: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(str(local.get("id") or "-"), width=60),
                _row_cell(local.get("name") or "-", expand=3),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, local=local: abrir_edicao_location(local),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, id=local.get("id"): [
                                    service.delete(id),
                                    on_refresh(None),
                                    event_bus.publish("locations_changed"),
                                    event_bus.mark_dirty("/inventory-events"),
                                ],
                            ),
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    width=120,
                    padding=ft.padding.symmetric(vertical=4, horizontal=0),
                    alignment=ft.alignment.center_right,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
            ],
            spacing=0,
        )
        return ft.Container(
            content=row,
            border=ft.border.only(bottom=ft.BorderSide(1, line_color)),
        )

    for local in locais:
        def abrir_edicao_location(local=local):
            dlg_name = ft.TextField(label=FIELD_NAME, value=local["name"])
            theme = page.theme
            error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
            dlg_required_msg = ft.Text("", color=error_color)
            def salvar_edicao(e, dlg):
                result = service.update(
                    local["id"],
                    (dlg_name.value or "").strip(),
                )
                if not result.ok:
                    if result.error_code == "VALIDATION_ERROR":
                        dlg_required_msg.value = "Informacoes obrigatorias"
                        dlg_name.border_color = error_color
                        dlg_name.focused_border_color = error_color
                        dlg_name.update()
                        dlg_required_msg.update()
                    return
                dlg.open = False
                page.update()
                on_refresh(None)
                event_bus.publish("locations_changed")
                event_bus.mark_dirty("/inventory-events")

            open_form_dialog(
                page,
                LOCATION_EDIT_TITLE,
                form_column([dlg_name, dlg_required_msg]),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=250,
            )

        list_view.controls.append(_build_grid_row(local))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
