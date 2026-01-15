# desktop/views/management/role_view.py

"""
Responsibilities:
- Render the role view.
- Wire UI events and interactions.
"""

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
from desktop.utils.list_row import build_list_row


def render_role_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
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

        coluna.controls.append(
            build_list_row(
                f"{role['id']} - {role['name']}",
                [
                    action_button(
                        ICON_EDIT,
                        page.theme.color_scheme.primary,
                        lambda e, role=role: abrir_edicao_role(role),
                    ),
                    action_button(
                        ICON_DELETE,
                        page.theme.color_scheme.error,
                        lambda e, id=role["id"]: [role_delete(id), on_refresh(None)],
                    ),
                ],
            )
        )

    return coluna
