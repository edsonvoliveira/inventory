# desktop/views/management/product_category_view.py

"""
Responsibilities:
- Render the product category view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.product_category_service import ProductCategoryService
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    CATEGORY_ADD,
    CATEGORY_ADD_TITLE,
    CATEGORY_EDIT_TITLE,
    CATEGORY_TITLE,
    DIALOG_CONFIRM_DELETE,
    FIELD_CODE,
    FIELD_DESCRIPTION,
    FIELD_NAME,
)
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.utils.dialogs import action_button, confirm_dialog, form_column, open_form_dialog


def render_product_category_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    service = ProductCategoryService()
    result = service.list()
    categorias = result.data or []

    if not result.ok:
        list_view.controls.append(ft.Text(result.message or "Erro ao carregar categorias."))

    def criar_categoria(e):
        dlg_code = ft.TextField(label=FIELD_CODE, autofocus=True)
        dlg_name = ft.TextField(label=FIELD_NAME)
        dlg_description = ft.TextField(label=FIELD_DESCRIPTION)
        theme = page.theme
        error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
        dlg_required_msg = ft.Text("", color=error_color)

        def _set_required_styles(missing: bool):
            color = error_color if missing else None
            dlg_code.border_color = color
            dlg_name.border_color = color
            dlg_code.focused_border_color = color
            dlg_name.focused_border_color = color

        def salvar_categoria(e, dlg):
            result = service.create(
                dlg_code.value or "",
                dlg_name.value or "",
                dlg_description.value,
            )
            if not result.ok:
                if result.error_code == "VALIDATION_ERROR":
                    dlg_required_msg.value = "Informacoes obrigatorias"
                    _set_required_styles(True)
                    dlg_code.update()
                    dlg_name.update()
                    dlg_required_msg.update()
                return
            dlg_required_msg.value = ""
            _set_required_styles(False)
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            CATEGORY_ADD_TITLE,
            form_column([dlg_code, dlg_name, dlg_description, dlg_required_msg]),
            salvar_categoria,
            BTN_CREATE,
            width=500,
            height=280,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(CATEGORY_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{CATEGORY_ADD}  ", icon=ICON_ADD, on_click=criar_categoria),
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
                    _header_cell("Codigo", width=120),
                    _header_cell("Nome", expand=2),
                    _header_cell("Descricao", expand=3),
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

    def _build_grid_row(categoria: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(categoria.get("code", "") or "-", width=120),
                _row_cell(categoria.get("name", "") or "-", expand=2),
                _row_cell(categoria.get("description", "") or "-", expand=3),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, categoria=categoria: abrir_edicao_categoria(categoria),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, categoria=categoria: confirm_dialog(
                                    page,
                                    DIALOG_CONFIRM_DELETE,
                                    lambda: [service.delete(categoria.get("uuid") or ""), on_refresh(None)],
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

    for categoria in categorias:
        def abrir_edicao_categoria(categoria=categoria):
            dlg_code = ft.TextField(label=FIELD_CODE, value=categoria.get("code") or "")
            dlg_name = ft.TextField(label=FIELD_NAME, value=categoria.get("name") or "")
            dlg_description = ft.TextField(label=FIELD_DESCRIPTION, value=categoria.get("description") or "")
            theme = page.theme
            error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
            dlg_required_msg = ft.Text("", color=error_color)

            def _set_required_styles(missing: bool):
                color = error_color if missing else None
                dlg_code.border_color = color
                dlg_name.border_color = color
                dlg_code.focused_border_color = color
                dlg_name.focused_border_color = color

            def salvar_edicao(e, dlg):
                result = service.update(
                    categoria.get("uuid") or "",
                    dlg_code.value or "",
                    dlg_name.value or "",
                    dlg_description.value,
                )
                if not result.ok:
                    if result.error_code == "VALIDATION_ERROR":
                        dlg_required_msg.value = "Informacoes obrigatorias"
                        _set_required_styles(True)
                        dlg_code.update()
                        dlg_name.update()
                        dlg_required_msg.update()
                    return
                dlg_required_msg.value = ""
                _set_required_styles(False)
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                CATEGORY_EDIT_TITLE,
                form_column([dlg_code, dlg_name, dlg_description, dlg_required_msg]),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=280,
            )

        list_view.controls.append(_build_grid_row(categoria))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
