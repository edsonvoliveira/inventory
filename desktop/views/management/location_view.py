# desktop/views/management/location_view.py

"""
Responsibilities:
- Render the location view.
- Wire UI events and interactions.
"""

import flet as ft

from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    FIELD_COMPANY,
    FIELD_NAME,
    HINT_LOCATION_NAME,
    LOCATION_ADD,
    LOCATION_ADD_TITLE,
    LOCATION_EDIT_TITLE,
    LOCATION_TITLE,
)
from desktop.data.repository import company_get_all, location_create, location_delete, location_get_all, location_update
from desktop.utils.dialogs import action_button, form_column, open_form_dialog
from desktop.utils.validation import is_required
from desktop.utils.list_row import build_list_row


def render_location_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    locais = location_get_all()
    companies = company_get_all()

    def criar_local(e):
        dlg_name = ft.TextField(label=FIELD_NAME, hint_text=HINT_LOCATION_NAME, autofocus=True)
        dlg_company = ft.Dropdown(
            label=FIELD_COMPANY,
            options=[ft.dropdown.Option(str(c["id"]), c["name"]) for c in companies],
        )

        def salvar_local(e, dlg):
            nome = dlg_name.value or ""
            if not is_required(nome) or not dlg_company.value:
                return
            location_create(nome.strip(), int(dlg_company.value))
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            LOCATION_ADD_TITLE,
            form_column([dlg_name, dlg_company]),
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

    for local in locais:
        def abrir_edicao_location(local=local):
            dlg_name = ft.TextField(label=FIELD_NAME, value=local["name"])
            dlg_company = ft.Dropdown(
                label=FIELD_COMPANY,
                options=[ft.dropdown.Option(str(c["id"]), c["name"]) for c in companies],
                value=str(local["company_id"]),
            )
            def salvar_edicao(e, dlg):
                location_update(
                    local["id"],
                    (dlg_name.value or "").strip(),
                    int(dlg_company.value or 0),
                )
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                LOCATION_EDIT_TITLE,
                form_column([dlg_name, dlg_company]),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=250,
            )

        coluna.controls.append(
            build_list_row(
                f"{local['id']} - {local['name']}",
                [
                    action_button(
                        ICON_EDIT,
                        page.theme.color_scheme.primary,
                        lambda e, local=local: abrir_edicao_location(local),
                    ),
                    action_button(
                        ICON_DELETE,
                        page.theme.color_scheme.error,
                        lambda e, id=local["id"]: [location_delete(id), on_refresh(None)],
                    ),
                ],
            )
        )

    return coluna
