# desktop/views/management/product_view.py

"""
Responsibilities:
- Render the product view.
- Wire UI events and interactions.
"""

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
from desktop.utils.dialogs import action_button, confirm_dialog, form_column, open_form_dialog
from desktop.utils.list_row import build_list_row


def render_product_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    product_service = ProductService()
    products_result = product_service.list()
    produtos = products_result.data or []

    if not products_result.ok:
        coluna.controls.append(ft.Text(products_result.message or "Erro ao carregar produtos."))

    def criar_produto(e):
        dlg_sku = ft.TextField(label=FIELD_SKU, hint_text=HINT_PRODUCT_SKU, autofocus=True)
        dlg_barcode = ft.TextField(label=FIELD_BARCODE, hint_text=HINT_PRODUCT_BARCODE)
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_PRODUCT_NAME)
        dlg_unit_cost = ft.TextField(label=FIELD_PRICE, hint_text=HINT_PRICE)
        dlg_unit_of_measure = ft.TextField(label=FIELD_UNIT, hint_text=HINT_UNIT)
        dlg_required_msg = ft.Text("", color=page.theme.color_scheme.error)

        def _set_required_styles(missing: bool):
            color = page.theme.color_scheme.error if missing else None
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

    for produto in produtos:
        def abrir_edicao_product(produto=produto):
            dlg_sku = ft.TextField(label=FIELD_SKU, value=produto["sku"])
            dlg_barcode = ft.TextField(label=FIELD_BARCODE, value=produto["barcode"] or "")
            dlg_name = ft.TextField(label=FIELD_NAME, value=produto["name"])
            dlg_unit_cost = ft.TextField(label=FIELD_PRICE, value=str(produto["unit_cost"]))
            dlg_unit_of_measure = ft.TextField(label=FIELD_UNIT, value=produto["unit_of_measure"])
            dlg_required_msg = ft.Text("", color=page.theme.color_scheme.error)

            def _set_required_styles(missing: bool):
                color = page.theme.color_scheme.error if missing else None
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

        coluna.controls.append(
            build_list_row(
                f"{produto['id']} - {produto['sku']} - {produto['name']}",
                [
                    action_button(
                        ICON_EDIT,
                        page.theme.color_scheme.primary,
                        lambda e, produto=produto: abrir_edicao_product(produto),
                    ),
                    action_button(
                        ICON_DELETE,
                        page.theme.color_scheme.error,
                        lambda e, id=produto["id"]: confirm_dialog(
                            page,
                            DIALOG_CONFIRM_DELETE,
                            lambda: [product_service.delete(id), on_refresh(None)],
                        ),
                    ),
                ],
            )
        )

    return coluna
