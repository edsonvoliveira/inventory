# desktop/views/management/user_view.py

"""
Responsibilities:
- Render the user view.
- Wire UI events and interactions.
"""

import flet as ft

from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    FIELD_ACTIVE,
    FIELD_COMPANY,
    FIELD_EMAIL,
    FIELD_ROLE,
    HINT_USER_EMAIL,
    USER_ADD,
    USER_ADD_TITLE,
    USER_EDIT_TITLE,
    USER_TITLE,
)
from desktop.data.repository import (
    company_get_all,
    role_get_all,
    user_create,
    user_delete,
    user_get_all,
    user_update,
)
from desktop.utils.dialogs import action_button, form_column, open_form_dialog
from desktop.utils.validation import is_required
from desktop.utils.list_row import build_list_row


def render_user_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    usuarios = user_get_all()
    roles = role_get_all()
    companies = company_get_all()

    def criar_usuario(e):
        dlg_email = ft.TextField(label=FIELD_EMAIL, hint_text=HINT_USER_EMAIL, autofocus=True)
        dlg_role = ft.Dropdown(
            label=FIELD_ROLE,
            options=[ft.dropdown.Option(str(r["id"]), r["name"]) for r in roles],
        )
        dlg_company = ft.Dropdown(
            label=FIELD_COMPANY,
            options=[ft.dropdown.Option(str(c["id"]), c["name"]) for c in companies],
        )

        def salvar_usuario(e, dlg):
            email = dlg_email.value or ""
            if not is_required(email) or not dlg_role.value or not dlg_company.value:
                return
            user_create(email.strip(), int(dlg_role.value), int(dlg_company.value))
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            USER_ADD_TITLE,
            form_column([dlg_email, dlg_company, dlg_role]),
            salvar_usuario,
            BTN_CREATE,
            width=500,
            height=250,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(USER_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{USER_ADD}  ", icon=ICON_ADD, on_click=criar_usuario),
            ],
            spacing=5,
        )
    )

    for usuario in usuarios:
        def abrir_edicao_user(usuario=usuario):
            dlg_email = ft.TextField(label=FIELD_EMAIL, value=usuario["email"])
            dlg_role = ft.Dropdown(
                label=FIELD_ROLE,
                options=[ft.dropdown.Option(str(r["id"]), r["name"]) for r in roles],
                value=str(usuario["role_id"]),
            )
            dlg_company = ft.Dropdown(
                label=FIELD_COMPANY,
                options=[ft.dropdown.Option(str(c["id"]), c["name"]) for c in companies],
                value=str(usuario["company_id"]),
            )
            dlg_active = ft.Checkbox(label=FIELD_ACTIVE, value=bool(usuario["is_active"]))
            def salvar_edicao(e, dlg):
                user_update(
                    usuario["id"],
                    (dlg_email.value or "").strip(),
                    int(dlg_role.value or 0),
                    int(dlg_company.value or 0),
                    int(dlg_active.value or 0),
                )
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                USER_EDIT_TITLE,
                form_column([dlg_email, dlg_company, dlg_role, dlg_active]),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=250,
            )

        coluna.controls.append(
            build_list_row(
                f"{usuario['id']} - {usuario['email']}",
                [
                    action_button(
                        ICON_EDIT,
                        page.theme.color_scheme.primary,
                        lambda e, usuario=usuario: abrir_edicao_user(usuario),
                    ),
                    action_button(
                        ICON_DELETE,
                        page.theme.color_scheme.error,
                        lambda e, id=usuario["id"]: [user_delete(id), on_refresh(None)],
                    ),
                ],
            )
        )

    return coluna
