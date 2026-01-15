import flet as ft

from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    COMPANY_ADD,
    COMPANY_ADD_TITLE,
    COMPANY_EDIT_TITLE,
    COMPANY_TITLE,
    BTN_CREATE,
    BTN_SAVE,
    ERROR_REQUIRED_NAME,
    FIELD_NAME,
    FIELD_NIF,
    HINT_COMPANY_NAME,
    HINT_NIF,
)
from desktop.data.repository import company_create, company_delete, company_get_all, company_update
from desktop.utils.dialogs import action_button, form_column, open_form_dialog
from desktop.utils.validation import is_required
from desktop.utils.list_row import build_list_row


def render_company_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    empresas = company_get_all()

    def criar_empresa(e):
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_COMPANY_NAME, autofocus=True)
        dlg_nif = ft.TextField(label=FIELD_NIF, hint_text=HINT_NIF)

        def salvar_nova_empresa(e, dlg):
            nome = dlg_name.value or ""
            nif = dlg_nif.value.strip() if dlg_nif.value else None

            if not is_required(nome):
                dlg_name.error_text = ERROR_REQUIRED_NAME
                dlg_name.update()
                return

            company_create(nome.strip(), nif)
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

    for emp in empresas:
        def abrir_edicao_empresa(emp=emp):
            dlg_name = ft.TextField(label=FIELD_NAME, value=emp["name"])
            dlg_nif = ft.TextField(label=FIELD_NIF, value=emp["nif"] or "")
            def salvar_edicao(e, dlg):
                company_update(
                    emp["id"],
                    (dlg_name.value or "").strip(),
                    (dlg_nif.value or "").strip() or None,
                )
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

        coluna.controls.append(
            build_list_row(
                f"{emp['id']} - {emp['name']} - {emp['nif'] or ''}",
                [
                    action_button(
                        ICON_EDIT,
                        page.theme.color_scheme.primary,
                        lambda e, emp=emp: abrir_edicao_empresa(emp),
                    ),
                    action_button(
                        ICON_DELETE,
                        page.theme.color_scheme.error,
                        lambda e, id=emp["id"]: [company_delete(id), on_refresh(None)],
                    ),
                ],
            )
        )

    return coluna
