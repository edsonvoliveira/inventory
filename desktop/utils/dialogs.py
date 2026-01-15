import flet as ft

from desktop.core.strings import BTN_CANCEL


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


def action_button(icon: str, color: str, on_click):
    return ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(name=icon, color=color)],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        on_click=on_click,
    )
