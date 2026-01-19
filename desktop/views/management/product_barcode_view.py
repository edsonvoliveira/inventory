# desktop/views/management/product_barcode_view.py

"""
Responsibilities:
- Render the product barcode view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.product_barcode_service import ProductBarcodeService
from desktop.core.strings import (
    BARCODE_ADD,
    BARCODE_ADD_TITLE,
    BARCODE_EDIT_TITLE,
    BARCODE_TITLE,
    BTN_CREATE,
    BTN_SAVE,
    DIALOG_CONFIRM_DELETE,
    FIELD_DESCRIPTION,
    FIELD_PRODUCT,
)
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.utils.dialogs import action_button, confirm_dialog, form_column, open_form_dialog


def _product_options() -> list[ft.dropdown.Option]:
    options: list[ft.dropdown.Option] = []
    for row in ProductsRepo().get_all():
        server_id = row.get("server_id")
        name = row.get("name") or ""
        sku = row.get("sku") or ""
        if server_id is None:
            continue
        options.append(ft.dropdown.Option(str(server_id), f"{sku} - {name}".strip(" -")))
    return options


def render_product_barcode_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    service = ProductBarcodeService()
    result = service.list()
    codigos = result.data or []
    product_options = _product_options()

    if not result.ok:
        list_view.controls.append(ft.Text(result.message or "Erro ao carregar codigos."))

    def criar_codigo(e):
        dlg_product = ft.Dropdown(label=FIELD_PRODUCT, options=product_options)
        dlg_barcode = ft.TextField(label="Codigo de Barras")
        dlg_description = ft.TextField(label=FIELD_DESCRIPTION)
        theme = page.theme
        error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
        dlg_required_msg = ft.Text("", color=error_color)

        def _set_required_styles(missing: bool):
            color = error_color if missing else None
            dlg_product.border_color = color
            dlg_barcode.border_color = color
            dlg_product.focused_border_color = color
            dlg_barcode.focused_border_color = color

        def salvar_codigo(e, dlg):
            result = service.create(
                dlg_product.value,
                dlg_barcode.value or "",
                dlg_description.value,
            )
            if not result.ok:
                if result.error_code == "VALIDATION_ERROR":
                    dlg_required_msg.value = "Informacoes obrigatorias"
                    _set_required_styles(True)
                    dlg_product.update()
                    dlg_barcode.update()
                    dlg_required_msg.update()
                return
            dlg_required_msg.value = ""
            _set_required_styles(False)
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            BARCODE_ADD_TITLE,
            form_column([dlg_product, dlg_barcode, dlg_description, dlg_required_msg]),
            salvar_codigo,
            BTN_CREATE,
            width=500,
            height=280,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(BARCODE_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{BARCODE_ADD}  ", icon=ICON_ADD, on_click=criar_codigo),
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
                    _header_cell("Codigo", width=140),
                    _header_cell("Produto", width=120),
                    _header_cell("Descricao", expand=2),
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

    def _build_grid_row(codigo: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(codigo.get("barcode", "") or "-", width=140),
                _row_cell(str(codigo.get("product_server_id") or "-"), width=120),
                _row_cell(codigo.get("description", "") or "-", expand=2),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, codigo=codigo: abrir_edicao(codigo),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, codigo=codigo: confirm_dialog(
                                    page,
                                    DIALOG_CONFIRM_DELETE,
                                    lambda: [service.delete(codigo.get("uuid") or ""), on_refresh(None)],
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

    for codigo in codigos:
        def abrir_edicao(codigo=codigo):
            dlg_product = ft.Dropdown(
                label=FIELD_PRODUCT,
                options=product_options,
                value=str(codigo.get("product_server_id") or ""),
            )
            dlg_barcode = ft.TextField(label="Codigo de Barras", value=codigo.get("barcode") or "")
            dlg_description = ft.TextField(label=FIELD_DESCRIPTION, value=codigo.get("description") or "")
            theme = page.theme
            error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
            dlg_required_msg = ft.Text("", color=error_color)

            def _set_required_styles(missing: bool):
                color = error_color if missing else None
                dlg_product.border_color = color
                dlg_barcode.border_color = color
                dlg_product.focused_border_color = color
                dlg_barcode.focused_border_color = color

            def salvar_edicao(e, dlg):
                result = service.update(
                    codigo.get("uuid") or "",
                    dlg_product.value,
                    dlg_barcode.value or "",
                    dlg_description.value,
                )
                if not result.ok:
                    if result.error_code == "VALIDATION_ERROR":
                        dlg_required_msg.value = "Informacoes obrigatorias"
                        _set_required_styles(True)
                        dlg_product.update()
                        dlg_barcode.update()
                        dlg_required_msg.update()
                    return
                dlg_required_msg.value = ""
                _set_required_styles(False)
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                BARCODE_EDIT_TITLE,
                form_column([dlg_product, dlg_barcode, dlg_description, dlg_required_msg]),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=280,
            )

        list_view.controls.append(_build_grid_row(codigo))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
