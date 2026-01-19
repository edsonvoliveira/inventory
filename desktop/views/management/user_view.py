# desktop/views/management/user_view.py

"""
Responsibilities:
- Render the user view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

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


def render_user_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
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
                    _header_cell("Email", expand=3),
                    _header_cell("Empresa", expand=2),
                    _header_cell("Role", width=120),
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

    def _build_grid_row(usuario: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(str(usuario.get("id") or "-"), width=60),
                _row_cell(usuario.get("email") or "-", expand=3),
                _row_cell(str(usuario.get("company_id") or "-"), expand=2),
                _row_cell(str(usuario.get("role_id") or "-"), width=120),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, usuario=usuario: abrir_edicao_user(usuario),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, id=usuario.get("id"): [user_delete(id), on_refresh(None)],
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

        list_view.controls.append(_build_grid_row(usuario))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
