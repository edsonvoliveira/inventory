# desktop/utils/dialogs.py

"""
Responsibilities:
- Utility helpers for dialogs.
- Provide shared helper functions.
"""

import flet as ft

from desktop.core.strings import (
    BTN_CANCEL,
    BTN_CONFIRM,
    DIALOG_CONFIRM_TITLE,
    DIALOG_ERROR_TITLE,
    DIALOG_SUCCESS_TITLE,
)


def form_column(controls: list[ft.Control], spacing: int = 10):
    return ft.Column(controls, spacing=spacing)


def open_form_dialog(
    page: ft.Page,
    title: str,
    content: ft.Control,
    on_submit,
    submit_label: str,
    width: int = 500,
    height: int = 250,
):
    def handle_submit(e):
        on_submit(e, dlg)

    dlg = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Container(content=content, width=width, height=height),
        actions=[
            ft.TextButton(BTN_CANCEL, on_click=lambda e: [setattr(dlg, "open", False), page.update()]),
            ft.ElevatedButton(submit_label, on_click=handle_submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=10),
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    return dlg


def action_button(icon: str, color: str, on_click, disabled: bool = False):
    return ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(name=icon, color=color)],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        on_click=None if disabled else on_click,
        disabled=disabled,
    )


def disable_control(control: ft.Control) -> None:
    if hasattr(control, "disabled"):
        control.disabled = True
    if hasattr(control, "border_color"):
        control.border_color = ft.Colors.GREY_300
    if hasattr(control, "focused_border_color"):
        control.focused_border_color = ft.Colors.GREY_300
    if hasattr(control, "label_style"):
        control.label_style = ft.TextStyle(color=ft.Colors.GREY_400)
    if hasattr(control, "text_style"):
        control.text_style = ft.TextStyle(color=ft.Colors.GREY_400)


def confirm_dialog(
    page: ft.Page,
    message: str,
    on_confirm,
    title: str = DIALOG_CONFIRM_TITLE,
):
    def handle_confirm(e):
        dlg.open = False
        page.update()
        on_confirm()

    dlg = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton(BTN_CANCEL, on_click=lambda e: [setattr(dlg, "open", False), page.update()]),
            ft.ElevatedButton(BTN_CONFIRM, on_click=handle_confirm),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=10),
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    return dlg


def error_dialog(
    page: ft.Page,
    message: str,
    title: str = DIALOG_ERROR_TITLE,
):
    dlg = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[ft.TextButton(BTN_CANCEL, on_click=lambda e: [setattr(dlg, "open", False), page.update()])],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=10),
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    return dlg


def success_dialog(
    page: ft.Page,
    message: str,
    title: str = DIALOG_SUCCESS_TITLE,
):
    dlg = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[ft.TextButton(BTN_CONFIRM, on_click=lambda e: [setattr(dlg, "open", False), page.update()])],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=10),
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    return dlg
