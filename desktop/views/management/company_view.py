# desktop/views/management/company_view.py

"""
Responsibilities:
- Render the company view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.company_service import CompanyService
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    COMPANY_ADD,
    COMPANY_ADD_TITLE,
    COMPANY_EDIT_TITLE,
    COMPANY_TITLE,
    BTN_CREATE,
    BTN_SAVE,
    DIALOG_CONFIRM_DELETE,
    ERROR_REQUIRED_NAME,
    FIELD_NAME,
    FIELD_NIF,
    HINT_COMPANY_NAME,
    HINT_NIF,
)
from desktop.utils.dialogs import action_button, confirm_dialog, form_column, open_form_dialog


def render_company_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    service = CompanyService()
    result = service.list()
    empresas = result.data or []

    if not result.ok:
        list_view.controls.append(ft.Text(result.message or "Erro ao carregar empresas."))

    def criar_empresa(e):
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_COMPANY_NAME, autofocus=True)
        dlg_nif = ft.TextField(label=FIELD_NIF, hint_text=HINT_NIF)

        def salvar_nova_empresa(e, dlg):
            nome = dlg_name.value or ""
            nif = dlg_nif.value.strip() if dlg_nif.value else None

            result = service.create(nome, nif)
            if not result.ok:
                dlg_name.error_text = result.message or ERROR_REQUIRED_NAME
                dlg_name.update()
                return

            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            COMPANY_ADD_TITLE,
            form_column([dlg_name, dlg_nif]),
            salvar_nova_empresa,
            BTN_CREATE,
            width=400,
            height=200,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(COMPANY_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{COMPANY_ADD}  ", icon=ICON_ADD, on_click=criar_empresa),
            ],
            spacing=5,
        ),
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
                    _header_cell("Nome", expand=2),
                    _header_cell("NIF", width=140),
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

    def _build_grid_row(emp: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(str(emp.get("id") or "-"), width=60),
                _row_cell(emp.get("name") or "-", expand=2),
                _row_cell(emp.get("nif") or "-", width=140),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, emp=emp: abrir_edicao_empresa(emp),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, id=emp.get("id"): confirm_dialog(
                                    page,
                                    DIALOG_CONFIRM_DELETE,
                                    lambda: [service.delete(id), on_refresh(None)],
                                ),
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

    for emp in empresas:
        def abrir_edicao_empresa(emp=emp):
            dlg_name = ft.TextField(label=FIELD_NAME, value=emp["name"])
            dlg_nif = ft.TextField(label=FIELD_NIF, value=emp["nif"] or "")
            def salvar_edicao(e, dlg):
                result = service.update(
                    emp["id"],
                    (dlg_name.value or "").strip(),
                    (dlg_nif.value or "").strip() or None,
                )
                if not result.ok:
                    dlg_name.error_text = result.message or ERROR_REQUIRED_NAME
                    dlg_name.update()
                    return
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                COMPANY_EDIT_TITLE,
                form_column([dlg_name, dlg_nif]),
                salvar_edicao,
                BTN_SAVE,
                width=400,
                height=250,
            )

        list_view.controls.append(_build_grid_row(emp))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
