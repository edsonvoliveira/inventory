import flet as ft
from datetime import datetime

from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    ERROR_INVALID_PRICE,
    FIELD_BARCODE,
    FIELD_COMPANY,
    FIELD_NAME,
    FIELD_PRICE,
    FIELD_SKU,
    FIELD_UNIT,
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
from desktop.data.repository import company_get_all, product_create, product_delete, product_get_all, product_update
from desktop.utils.dialogs import action_button, form_column, open_form_dialog
from desktop.utils.validation import is_required, parse_float
from desktop.utils.list_row import build_list_row


def render_product_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    produtos = product_get_all()
    companies = company_get_all()

    def criar_produto(e):
        dlg_sku = ft.TextField(label=FIELD_SKU, hint_text=HINT_PRODUCT_SKU, autofocus=True)
        dlg_barcode = ft.TextField(label=FIELD_BARCODE, hint_text=HINT_PRODUCT_BARCODE)
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_PRODUCT_NAME)
        dlg_unit_cost = ft.TextField(label=FIELD_PRICE, hint_text=HINT_PRICE)
        dlg_unit_of_measure = ft.TextField(label=FIELD_UNIT, hint_text=HINT_UNIT)
        dlg_company = ft.Dropdown(
            label=FIELD_COMPANY,
            options=[ft.dropdown.Option(str(c["id"]), c["name"]) for c in companies],
        )

        def salvar_produto(e, dlg):
            sku = dlg_sku.value or ""
            name = dlg_name.value or ""
            barcode = dlg_barcode.value.strip() if dlg_barcode.value else ""
            unit_of_measure = dlg_unit_of_measure.value.strip() if dlg_unit_of_measure.value else "UN"
            if not is_required(sku) or not is_required(name) or not dlg_company.value:
                return
            unit_cost = parse_float(dlg_unit_cost.value)
            if unit_cost is None:
                dlg_unit_cost.error_text = ERROR_INVALID_PRICE
                dlg_unit_cost.update()
                return
            product_create(
                sku.strip(),
                barcode,
                name.strip(),
                unit_cost,
                unit_of_measure,
                datetime.now().isoformat(),
                int(dlg_company.value),
            )
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            PRODUCT_ADD_TITLE,
            form_column([dlg_sku, dlg_barcode, dlg_name, dlg_unit_cost, dlg_unit_of_measure, dlg_company]),
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
            dlg_company = ft.Dropdown(
                label=FIELD_COMPANY,
                options=[ft.dropdown.Option(str(c["id"]), c["name"]) for c in companies],
                value=str(produto["company_id"]),
            )
            def salvar_edicao(e, dlg):
                product_update(
                    produto["id"],
                    (dlg_sku.value or "").strip(),
                    (dlg_barcode.value or "").strip(),
                    (dlg_name.value or "").strip(),
                    float(dlg_unit_cost.value or 0),
                    (dlg_unit_of_measure.value or "").strip(),
                    datetime.now().isoformat(),
                    int(dlg_company.value or 0),
                )
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                PRODUCT_EDIT_TITLE,
                form_column([dlg_sku, dlg_barcode, dlg_name, dlg_unit_cost, dlg_unit_of_measure, dlg_company]),
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
                        lambda e, id=produto["id"]: [product_delete(id), on_refresh(None)],
                    ),
                ],
            )
        )

    return coluna
