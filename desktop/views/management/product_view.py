# desktop/views/management/product_view.py

"""
Responsibilities:
- Render the product view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.product_service import ProductService
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    ERROR_INVALID_PRICE,
    FIELD_BARCODE,
    FIELD_NAME,
    FIELD_PRICE,
    FIELD_SKU,
    FIELD_UNIT,
    DIALOG_CONFIRM_DELETE,
    HINT_PRICE,
    HINT_PRODUCT_BARCODE,
    HINT_PRODUCT_NAME,
    HINT_PRODUCT_SKU,
    HINT_UNIT,
    PRODUCT_ADD,
    PRODUCT_ADD_TITLE,
    PRODUCT_EDIT_TITLE,
    PRODUCT_TITLE,
)
from desktop.utils.dialogs import action_button, confirm_dialog, form_column, open_form_dialog, disable_control
from desktop.utils.event_bus import event_bus


def render_product_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    product_service = ProductService()
    products_result = product_service.list()
    produtos = products_result.data or []

    if not products_result.ok:
        list_view.controls.append(ft.Text(products_result.message or "Erro ao carregar produtos."))

    def criar_produto(e):
        dlg_sku = ft.TextField(label=FIELD_SKU, hint_text=HINT_PRODUCT_SKU, autofocus=True)
        dlg_barcode = ft.TextField(label=FIELD_BARCODE, hint_text=HINT_PRODUCT_BARCODE)
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_PRODUCT_NAME)
        dlg_unit_cost = ft.TextField(label=FIELD_PRICE, hint_text=HINT_PRICE)
        dlg_unit_of_measure = ft.TextField(label=FIELD_UNIT, hint_text=HINT_UNIT)
        theme = page.theme
        error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
        dlg_required_msg = ft.Text("", color=error_color)

        def _set_required_styles(missing: bool):
            color = error_color if missing else None
            dlg_sku.border_color = color
            dlg_name.border_color = color
            dlg_sku.focused_border_color = color
            dlg_name.focused_border_color = color

        def salvar_produto(e, dlg):
            sku = dlg_sku.value or ""
            name = dlg_name.value or ""
            barcode = dlg_barcode.value.strip() if dlg_barcode.value else ""
            unit_of_measure = dlg_unit_of_measure.value.strip() if dlg_unit_of_measure.value else "UN"
            result = product_service.create(
                sku,
                barcode,
                name,
                dlg_unit_cost.value or "",
                unit_of_measure,
            )
            if not result.ok:
                if result.error_code == "VALIDATION_ERROR":
                    dlg_required_msg.value = "Informacoes obrigatorias"
                    _set_required_styles(True)
                    dlg_sku.update()
                    dlg_name.update()
                    dlg_required_msg.update()
                if result.error_code == "INVALID_PRICE":
                    dlg_unit_cost.error_text = result.message
                    dlg_unit_cost.update()
                if result.error_code == "COMPANY_REQUIRED":
                    dlg_required_msg.value = result.message
                    dlg_required_msg.update()
                return
            dlg_required_msg.value = ""
            _set_required_styles(False)
            dlg.open = False
            page.update()
            on_refresh(None)
            event_bus.publish("products_changed")
            event_bus.publish("product_barcodes_changed")
            event_bus.mark_dirty("/product-barcodes")
            event_bus.mark_dirty("/event-targets")

        open_form_dialog(
            page,
            PRODUCT_ADD_TITLE,
            form_column(
                [dlg_sku, dlg_barcode, dlg_name, dlg_unit_cost, dlg_unit_of_measure, dlg_required_msg]
            ),
            salvar_produto,
            BTN_CREATE,
            width=500,
            height=250,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(PRODUCT_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{PRODUCT_ADD}  ", icon=ICON_ADD, on_click=criar_produto),
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
                    _header_cell("SKU", width=140),
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

    def _build_grid_row(produto: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(str(produto.get("id") or "-"), width=60),
                _row_cell(produto.get("sku") or "-", width=140),
                _row_cell(produto.get("name") or "-", expand=3),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, produto=produto: abrir_edicao_product(produto),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, id=produto.get("id"): confirm_dialog(
                                    page,
                                    DIALOG_CONFIRM_DELETE,
                                    lambda: [
                                        product_service.delete(id),
                                        on_refresh(None),
                                        event_bus.publish("products_changed"),
                                        event_bus.publish("product_barcodes_changed"),
                                        event_bus.mark_dirty("/product-barcodes"),
                                        event_bus.mark_dirty("/event-targets"),
                                    ],
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

    for produto in produtos:
        def abrir_edicao_product(produto=produto):
            dlg_sku = ft.TextField(label=FIELD_SKU, value=produto["sku"])
            dlg_barcode = ft.TextField(label=FIELD_BARCODE, value=produto["barcode"] or "")
            dlg_name = ft.TextField(label=FIELD_NAME, value=produto["name"])
            dlg_unit_cost = ft.TextField(label=FIELD_PRICE, value=str(produto["unit_cost"]))
            dlg_unit_of_measure = ft.TextField(label=FIELD_UNIT, value=produto["unit_of_measure"])
            disable_control(dlg_sku)
            disable_control(dlg_barcode)
            theme = page.theme
            error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
            dlg_required_msg = ft.Text("", color=error_color)

            def _set_required_styles(missing: bool):
                color = error_color if missing else None
                dlg_sku.border_color = color
                dlg_name.border_color = color
                dlg_sku.focused_border_color = color
                dlg_name.focused_border_color = color

            def salvar_edicao(e, dlg):
                result = product_service.update(
                    produto["id"],
                    dlg_sku.value or "",
                    (dlg_barcode.value or "").strip(),
                    dlg_name.value or "",
                    dlg_unit_cost.value or "",
                    dlg_unit_of_measure.value or "",
                )
                if not result.ok:
                    if result.error_code == "VALIDATION_ERROR":
                        dlg_required_msg.value = "Informacoes obrigatorias"
                        _set_required_styles(True)
                        dlg_sku.update()
                        dlg_name.update()
                        dlg_required_msg.update()
                    if result.error_code == "INVALID_PRICE":
                        dlg_unit_cost.error_text = result.message
                        dlg_unit_cost.update()
                    if result.error_code == "COMPANY_REQUIRED":
                        dlg_required_msg.value = result.message
                        dlg_required_msg.update()
                    return
                dlg_required_msg.value = ""
                _set_required_styles(False)
                dlg.open = False
                page.update()
                on_refresh(None)
                event_bus.publish("products_changed")
                event_bus.mark_dirty("/event-targets")
                if (dlg_barcode.value or "").strip():
                    event_bus.publish("product_barcodes_changed")
                    event_bus.mark_dirty("/product-barcodes")

            open_form_dialog(
                page,
                PRODUCT_EDIT_TITLE,
                form_column(
                    [dlg_sku, dlg_barcode, dlg_name, dlg_unit_cost, dlg_unit_of_measure, dlg_required_msg]
                ),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=250,
            )

        list_view.controls.append(_build_grid_row(produto))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
