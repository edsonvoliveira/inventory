# desktop/views/management/inventory_event_targets_view.py

"""
Responsibilities:
- Render the inventory event targets view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.inventory_event_target_service import InventoryEventTargetService
from desktop.core.sync_service import _get_sync_logger
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    DIALOG_CONFIRM_DELETE,
    FIELD_EVENT,
    FIELD_EXPECTED_QTY,
    FIELD_PRODUCT,
    TARGET_ADD,
    TARGET_ADD_TITLE,
    TARGET_EDIT_TITLE,
    TARGET_TITLE,
)
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.data.repositories.inventory_events_repo import InventoryEventsRepo
from desktop.data.repositories.products_repo import ProductsRepo
from desktop.utils.dialogs import action_button, confirm_dialog, form_column, open_form_dialog, disable_control
from desktop.utils.event_bus import event_bus
from desktop.utils.notifications import show_auto_refresh


def _event_options() -> list[ft.dropdown.Option]:
    options: list[ft.dropdown.Option] = []
    for row in InventoryEventsRepo().get_all():
        server_id = row.get("server_id")
        title = row.get("title") or ""
        if server_id is None:
            continue
        options.append(ft.dropdown.Option(str(server_id), title))
    return options


def _product_options() -> list[ft.dropdown.Option]:
    options: list[ft.dropdown.Option] = []
    for row in ProductsRepo().get_all():
        server_id = row.get("server_id")
        name = row.get("name") or ""
        sku = row.get("sku") or ""
        if server_id is None:
            continue
        options.append(ft.dropdown.Option(str(server_id), f"{sku} - {name}".strip(" -")))
    return options


def render_inventory_event_targets_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    service = InventoryEventTargetService()
    sync_logger = _get_sync_logger()
    result = service.list()
    targets = result.data or []
    def _on_products_changed(_payload):
        if page.route != "/event-targets":
            return
        on_refresh(None)
        show_auto_refresh(page)

    def _on_events_changed(_payload):
        if page.route != "/event-targets":
            return
        on_refresh(None)
        show_auto_refresh(page)

    event_bus.subscribe(
        "products_changed",
        _on_products_changed,
        key="inventory_event_targets_view.products",
    )
    event_bus.subscribe(
        "inventory_events_changed",
        _on_events_changed,
        key="inventory_event_targets_view.events",
    )
    if not result.ok:
        list_view.controls.append(ft.Text(result.message or "Erro ao carregar targets."))

    def criar_target(e):
        dlg_event = ft.Dropdown(label=FIELD_EVENT, options=_event_options())
        dlg_product = ft.Dropdown(label=FIELD_PRODUCT, options=_product_options())
        dlg_expected_qty = ft.TextField(label=FIELD_EXPECTED_QTY)
        theme = page.theme
        error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
        dlg_required_msg = ft.Text("", color=error_color)

        def _set_required_styles(missing: bool):
            color = error_color if missing else None
            dlg_event.border_color = color
            dlg_product.border_color = color
            dlg_event.focused_border_color = color
            dlg_product.focused_border_color = color

        def salvar_target(e, dlg):
            result = service.create(
                dlg_event.value,
                dlg_product.value,
                dlg_expected_qty.value,
            )
            if not result.ok:
                sync_logger.info(
                    "event=ui_event_target_create_failed error_code=%s message=%s event=%s product=%s",
                    result.error_code,
                    result.message,
                    dlg_event.value,
                    dlg_product.value,
                )
                if result.error_code == "VALIDATION_ERROR":
                    dlg_required_msg.value = "Informacoes obrigatorias"
                    _set_required_styles(True)
                    dlg_event.update()
                    dlg_product.update()
                    dlg_required_msg.update()
                return
            dlg_required_msg.value = ""
            _set_required_styles(False)
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            TARGET_ADD_TITLE,
            form_column([dlg_event, dlg_product, dlg_expected_qty, dlg_required_msg]),
            salvar_target,
            BTN_CREATE,
            width=500,
            height=280,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(TARGET_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{TARGET_ADD}  ", icon=ICON_ADD, on_click=criar_target),
            ],
            spacing=5,
        )
    )

    header_bg = getattr(ft.Colors, "BLUE_GREY_50", ft.Colors.GREY_200)
    line_color = getattr(ft.Colors, "BLUE_GREY_100", ft.Colors.GREY_300)

    def _header_cell(
        label: str,
        *,
        width: Optional[int] = None,
        expand: Optional[int] = None,
        align: Optional[ft.Alignment] = None,
        text_align: Optional[ft.TextAlign] = None,
    ):
        return ft.Container(
            content=ft.Text(label, weight=ft.FontWeight.BOLD, size=12, text_align=text_align),
            width=width,
            expand=expand,
            alignment=align,
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
                    _header_cell("Evento", width=120),
                    _header_cell("Produto", width=120),
                    _header_cell("Qtd Esperada", width=140),
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

    def _build_grid_row(target: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        row = ft.Row(
            [
                _row_cell(str(target.get("event_server_id") or "-"), width=120),
                _row_cell(str(target.get("product_server_id") or "-"), width=120),
                _row_cell(str(target.get("expected_qty") or "-"), width=140),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, target=target: abrir_edicao(target),
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, target=target: confirm_dialog(
                                    page,
                                    DIALOG_CONFIRM_DELETE,
                                    lambda: [service.delete(target.get("uuid") or ""), on_refresh(None)],
                                ),
                            ),
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    expand=1,
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

    for target in targets:
        def abrir_edicao(target=target):
            dlg_event = ft.Dropdown(
                label=FIELD_EVENT,
                options=_event_options(),
                value=str(target.get("event_server_id") or ""),
            )
            dlg_product = ft.Dropdown(
                label=FIELD_PRODUCT,
                options=_product_options(),
                value=str(target.get("product_server_id") or ""),
            )
            dlg_expected_qty = ft.TextField(label=FIELD_EXPECTED_QTY, value=str(target.get("expected_qty") or ""))
            disable_control(dlg_event)
            disable_control(dlg_product)
            theme = page.theme
            error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
            dlg_required_msg = ft.Text("", color=error_color)

            def _set_required_styles(missing: bool):
                color = error_color if missing else None
                dlg_event.border_color = color
                dlg_product.border_color = color
                dlg_event.focused_border_color = color
                dlg_product.focused_border_color = color

            def salvar_edicao(e, dlg):
                result = service.update(
                    target.get("uuid") or "",
                    dlg_event.value,
                    dlg_product.value,
                    dlg_expected_qty.value,
                )
                if not result.ok:
                    sync_logger.info(
                        "event=ui_event_target_update_failed error_code=%s message=%s uuid=%s",
                        result.error_code,
                        result.message,
                        target.get("uuid"),
                    )
                    if result.error_code == "VALIDATION_ERROR":
                        dlg_required_msg.value = "Informacoes obrigatorias"
                        _set_required_styles(True)
                        dlg_event.update()
                        dlg_product.update()
                        dlg_required_msg.update()
                    return
                dlg_required_msg.value = ""
                _set_required_styles(False)
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                TARGET_EDIT_TITLE,
                form_column([dlg_event, dlg_product, dlg_expected_qty, dlg_required_msg]),
                salvar_edicao,
                BTN_SAVE,
                width=500,
                height=280,
            )

        list_view.controls.append(_build_grid_row(target))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
