# desktop/views/management/inventory_events_view.py

"""
Responsibilities:
- Render the inventory events view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.inventory_event_service import InventoryEventService
from desktop.core.sync_service import _get_sync_logger
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    DIALOG_CONFIRM_DELETE,
    EVENT_ADD,
    EVENT_ADD_TITLE,
    EVENT_EDIT_TITLE,
    EVENT_TITLE,
    FIELD_EVENT_TYPE,
    FIELD_LOCATION,
    FIELD_REQUIRED_AUDITS,
    FIELD_REQUIRED_COUNTS,
    FIELD_STATUS,
    FIELD_TOLERANCE_ABSOLUTE,
    FIELD_TOLERANCE_PERCENT,
    FIELD_TITLE,
)
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.data.repositories.locations_repo import LocationsRepo
from desktop.utils.dialogs import action_button, confirm_dialog, form_column, open_form_dialog, disable_control
from desktop.utils.event_bus import event_bus
from desktop.utils.notifications import show_auto_refresh


def _location_options() -> list[ft.dropdown.Option]:
    options: list[ft.dropdown.Option] = []
    for row in LocationsRepo().get_all():
        server_id = row.get("server_id")
        name = row.get("name") or ""
        if server_id is None:
            continue
        options.append(ft.dropdown.Option(str(server_id), name))
    return options


def _status_options() -> list[ft.dropdown.Option]:
    return [
        ft.dropdown.Option("planned", "planned"),
        ft.dropdown.Option("open", "open"),
        ft.dropdown.Option("counting", "counting"),
        ft.dropdown.Option("closed", "closed"),
        ft.dropdown.Option("finalized", "finalized"),
    ]


def render_inventory_events_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    service = InventoryEventService()
    result = service.list()
    eventos = result.data or []
    status_by_id = {row.get("server_id"): row.get("status") for row in eventos if row.get("server_id") is not None}
    def _on_locations_changed(_payload):
        if page.route != "/inventory-events":
            return
        on_refresh(None)
        show_auto_refresh(page)

    event_bus.subscribe(
        "locations_changed",
        _on_locations_changed,
        key="inventory_events_view.locations",
    )
    if not result.ok:
        list_view.controls.append(ft.Text(result.message or "Erro ao carregar eventos."))

    def criar_evento(e):
        dlg_location = ft.Dropdown(label=FIELD_LOCATION, options=_location_options())
        dlg_title = ft.TextField(label=FIELD_TITLE, autofocus=True)
        dlg_event_type = ft.TextField(label=FIELD_EVENT_TYPE)
        dlg_status = ft.Dropdown(label=FIELD_STATUS, options=_status_options(), value="planned")
        dlg_required_counts = ft.TextField(label=FIELD_REQUIRED_COUNTS)
        dlg_required_audits = ft.TextField(label=FIELD_REQUIRED_AUDITS)
        dlg_tol_percent = ft.TextField(label=FIELD_TOLERANCE_PERCENT)
        dlg_tol_abs = ft.TextField(label=FIELD_TOLERANCE_ABSOLUTE)
        theme = page.theme
        error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
        dlg_required_msg = ft.Text("", color=error_color)

        def _set_required_styles(missing: bool):
            color = error_color if missing else None
            dlg_location.border_color = color
            dlg_title.border_color = color
            dlg_status.border_color = color
            dlg_location.focused_border_color = color
            dlg_title.focused_border_color = color
            dlg_status.focused_border_color = color

        def salvar_evento(e, dlg):
            result = service.create(
                dlg_location.value,
                dlg_title.value or "",
                dlg_event_type.value,
                dlg_status.value or "",
                dlg_required_counts.value,
                dlg_required_audits.value,
                dlg_tol_percent.value,
                dlg_tol_abs.value,
            )
            if not result.ok:
                _get_sync_logger().info(
                    "event=ui_inventory_event_create_failed error_code=%s message=%s location=%s title=%s status=%s",
                    result.error_code,
                    result.message,
                    dlg_location.value,
                    dlg_title.value,
                    dlg_status.value,
                )
                if result.error_code == "VALIDATION_ERROR":
                    dlg_required_msg.value = "Informacoes obrigatorias"
                    _set_required_styles(True)
                    dlg_location.update()
                    dlg_title.update()
                    dlg_status.update()
                    dlg_required_msg.update()
                elif result.error_code == "REQUIRED_COUNTS_NOT_MET":
                    dlg_required_msg.value = "Required counts nao atingido para fechar o evento."
                    dlg_required_msg.update()
                elif result.error_code == "OPERATION_NOT_ALLOWED_FOR_ORIGIN":
                    dlg_required_msg.value = "Operacao nao permitida."
                    dlg_required_msg.update()
                return
            dlg_required_msg.value = ""
            _set_required_styles(False)
            dlg.open = False
            page.update()
            on_refresh(None)
            event_bus.publish("inventory_events_changed")
            event_bus.mark_dirty("/zones")
            event_bus.mark_dirty("/event-targets")

        open_form_dialog(
            page,
            EVENT_ADD_TITLE,
            form_column(
                [
                    dlg_location,
                    dlg_title,
                    dlg_event_type,
                    dlg_status,
                    dlg_required_counts,
                    dlg_required_audits,
                    dlg_tol_percent,
                    dlg_tol_abs,
                    dlg_required_msg,
                ]
            ),
            salvar_evento,
            BTN_CREATE,
            width=520,
            height=360,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(EVENT_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{EVENT_ADD}  ", icon=ICON_ADD, on_click=criar_evento),
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
                    _header_cell("Titulo", expand=3),
                    _header_cell("Status", width=140),
                    _header_cell("Local", width=120),
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

    def _build_grid_row(evento: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        is_read_only = (evento.get("status") or "").lower() in {"closed", "finalized"}
        row = ft.Row(
            [
                _row_cell(evento.get("title") or "-", expand=3),
                _row_cell(evento.get("status") or "-", width=140),
                _row_cell(str(evento.get("location_server_id") or "-"), width=120),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, evento=evento: abrir_edicao(evento),
                                disabled=is_read_only,
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, evento=evento: confirm_dialog(
                                    page,
                                    DIALOG_CONFIRM_DELETE,
                                    lambda: [
                                        service.delete(evento.get("uuid") or ""),
                                        on_refresh(None),
                                        event_bus.publish("inventory_events_changed"),
                                        event_bus.mark_dirty("/zones"),
                                        event_bus.mark_dirty("/event-targets"),
                                    ],
                                ),
                                disabled=is_read_only,
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

    for evento in eventos:
        def abrir_edicao(evento=evento):
            if (evento.get("status") or "").lower() in {"closed", "finalized"}:
                return
            dlg_location = ft.Dropdown(
                label=FIELD_LOCATION,
                options=_location_options(),
                value=str(evento.get("location_server_id") or ""),
            )
            dlg_title = ft.TextField(label=FIELD_TITLE, value=evento.get("title") or "")
            dlg_event_type = ft.TextField(label=FIELD_EVENT_TYPE, value=evento.get("event_type") or "")
            dlg_status = ft.Dropdown(
                label=FIELD_STATUS,
                options=_status_options(),
                value=(evento.get("status") or "").lower() or "planned",
            )
            disable_control(dlg_location)
            dlg_required_counts = ft.TextField(label=FIELD_REQUIRED_COUNTS, value=str(evento.get("required_counts") or ""))
            dlg_required_audits = ft.TextField(label=FIELD_REQUIRED_AUDITS, value=str(evento.get("required_audits") or ""))
            dlg_tol_percent = ft.TextField(label=FIELD_TOLERANCE_PERCENT, value=str(evento.get("tolerance_percent") or ""))
            dlg_tol_abs = ft.TextField(label=FIELD_TOLERANCE_ABSOLUTE, value=str(evento.get("tolerance_absolute") or ""))
            theme = page.theme
            error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
            dlg_required_msg = ft.Text("", color=error_color)

            def _set_required_styles(missing: bool):
                color = error_color if missing else None
                dlg_location.border_color = color
                dlg_title.border_color = color
                dlg_status.border_color = color
                dlg_location.focused_border_color = color
                dlg_title.focused_border_color = color
                dlg_status.focused_border_color = color

            def salvar_edicao(e, dlg):
                result = service.update(
                    evento.get("uuid") or "",
                    dlg_location.value,
                    dlg_title.value or "",
                    dlg_event_type.value,
                    dlg_status.value or "",
                    dlg_required_counts.value,
                    dlg_required_audits.value,
                    dlg_tol_percent.value,
                    dlg_tol_abs.value,
                )
                if not result.ok:
                    _get_sync_logger().info(
                        "event=ui_inventory_event_update_failed error_code=%s message=%s uuid=%s status=%s",
                        result.error_code,
                        result.message,
                        evento.get("uuid") or "",
                        dlg_status.value,
                    )
                    if result.error_code == "VALIDATION_ERROR":
                        dlg_required_msg.value = "Informacoes obrigatorias"
                        _set_required_styles(True)
                        dlg_location.update()
                        dlg_title.update()
                        dlg_status.update()
                        dlg_required_msg.update()
                    elif result.error_code == "REQUIRED_COUNTS_NOT_MET":
                        dlg_required_msg.value = "Required counts nao atingido para fechar o evento."
                        dlg_required_msg.update()
                    elif result.error_code == "EVENT_READ_ONLY":
                        dlg_required_msg.value = "Evento fechado nao permite edicao."
                        dlg_required_msg.update()
                    elif result.error_code == "OPERATION_NOT_ALLOWED_FOR_ORIGIN":
                        dlg_required_msg.value = "Operacao nao permitida."
                        dlg_required_msg.update()
                    return
                dlg_required_msg.value = ""
                _set_required_styles(False)
                dlg.open = False
                page.update()
                on_refresh(None)
                event_bus.publish("inventory_events_changed")
                event_bus.mark_dirty("/zones")
                event_bus.mark_dirty("/event-targets")

            open_form_dialog(
                page,
                EVENT_EDIT_TITLE,
                form_column(
                    [
                        dlg_location,
                        dlg_title,
                        dlg_event_type,
                        dlg_status,
                        dlg_required_counts,
                        dlg_required_audits,
                        dlg_tol_percent,
                        dlg_tol_abs,
                        dlg_required_msg,
                    ]
                ),
                salvar_edicao,
                BTN_SAVE,
                width=520,
                height=360,
            )

        list_view.controls.append(_build_grid_row(evento))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
