# desktop/views/management/role_view.py

"""
Responsibilities:
- Render the role view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    ERROR_REQUIRED_NAME,
    FIELD_NAME,
    HINT_ROLE_NAME,
    ROLE_ADD,
    ROLE_ADD_TITLE,
    ROLE_EDIT_TITLE,
    ROLE_TITLE,
)
from desktop.data.repository import role_create, role_delete, role_get_all, role_update
from desktop.utils.dialogs import action_button, form_column, open_form_dialog
from desktop.utils.validation import is_required


def render_role_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    roles = role_get_all()

    def criar_role(e):
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_ROLE_NAME, autofocus=True)

        def salvar_role(e, dlg):
            nome = dlg_name.value or ""
            if not is_required(nome):
                dlg_name.error_text = ERROR_REQUIRED_NAME
                dlg_name.update()
                return
            role_create(nome.strip())
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            ROLE_ADD_TITLE,
            form_column([dlg_name]),
            salvar_role,
            BTN_CREATE,
            width=400,
            height=200,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(ROLE_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{ROLE_ADD}  ", icon=ICON_ADD, on_click=criar_role),
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

    def _build_grid_row(role: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(str(role.get("id") or "-"), width=60),
                _row_cell(role.get("name") or "-", expand=3),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, role=role: abrir_edicao_role(role),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, id=role.get("id"): [role_delete(id), on_refresh(None)],
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

    for role in roles:
        def abrir_edicao_role(role=role):
            dlg_name = ft.TextField(label=FIELD_NAME, value=role["name"])
            def salvar_edicao(e, dlg):
                role_update(role["id"], (dlg_name.value or "").strip())
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                ROLE_EDIT_TITLE,
                form_column([dlg_name]),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=200,
            )

        list_view.controls.append(_build_grid_row(role))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
