# desktop/views/management/zones_view.py

"""
Responsibilities:
- Render the zones view.
- Wire UI events and interactions.
"""

from typing import Any, Dict, Optional

import flet as ft

from desktop.core.zones_service import ZonesService
from desktop.core.sync_service import _get_sync_logger
from desktop.core.strings import (
    BTN_CREATE,
    BTN_SAVE,
    DIALOG_CONFIRM_DELETE,
    FIELD_DESCRIPTION,
    FIELD_EVENT,
    FIELD_NAME,
    FIELD_STATUS,
    ZONE_ADD,
    ZONE_ADD_TITLE,
    ZONE_EDIT_TITLE,
    ZONE_TITLE,
)
from desktop.core.ui_constants import ICON_ADD, ICON_DELETE, ICON_EDIT
from desktop.data.repositories.inventory_events_repo import InventoryEventsRepo
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


def render_zones_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    list_view = ft.ListView(expand=True, spacing=8)
    service = ZonesService()
    sync_logger = _get_sync_logger()
    result = service.list()
    zonas = result.data or []
    def _on_events_changed(_payload):
        if page.route != "/zones":
            return
        on_refresh(None)
        show_auto_refresh(page)

    event_bus.subscribe(
        "inventory_events_changed",
        _on_events_changed,
        key="zones_view.events",
    )
    event_status_by_id = {
        row.get("server_id"): (row.get("status") or "").lower()
        for row in InventoryEventsRepo().get_all()
        if row.get("server_id") is not None
    }

    if not result.ok:
        list_view.controls.append(ft.Text(result.message or "Erro ao carregar zonas."))

    def _count_status_options() -> list[ft.dropdown.Option]:
        return [
            ft.dropdown.Option("not_started", "not_started"),
            ft.dropdown.Option("counting", "counting"),
            ft.dropdown.Option("finished", "finished"),
        ]

    def _lock_status_options() -> list[ft.dropdown.Option]:
        return [
            ft.dropdown.Option("unlocked", "unlocked"),
            ft.dropdown.Option("locked", "locked"),
        ]

    def criar_zona(e):
        dlg_event = ft.Dropdown(label=FIELD_EVENT, options=_event_options())
        dlg_name = ft.TextField(label=FIELD_NAME, autofocus=True)
        dlg_description = ft.TextField(label=FIELD_DESCRIPTION)
        dlg_count_status = ft.Dropdown(
            label=f"{FIELD_STATUS} (Count)",
            options=_count_status_options(),
            value="not_started",
        )
        dlg_lock_status = ft.Dropdown(
            label=f"{FIELD_STATUS} (Lock)",
            options=_lock_status_options(),
            value="unlocked",
        )
        theme = page.theme
        error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
        dlg_required_msg = ft.Text("", color=error_color)

        def _set_required_styles(missing: bool):
            color = error_color if missing else None
            dlg_event.border_color = color
            dlg_name.border_color = color
            dlg_event.focused_border_color = color
            dlg_name.focused_border_color = color

        def salvar_zona(e, dlg):
            result = service.create(
                dlg_event.value,
                dlg_name.value or "",
                dlg_description.value,
                dlg_count_status.value,
                dlg_lock_status.value,
            )
            if not result.ok:
                sync_logger.info(
                    "event=ui_zone_create_failed error_code=%s message=%s event=%s name=%s",
                    result.error_code,
                    result.message,
                    dlg_event.value,
                    dlg_name.value,
                )
                if result.error_code == "VALIDATION_ERROR":
                    dlg_required_msg.value = "Informacoes obrigatorias"
                    _set_required_styles(True)
                    dlg_event.update()
                    dlg_name.update()
                    dlg_required_msg.update()
                elif result.error_code == "REQUIRED_COUNTS_NOT_MET":
                    dlg_required_msg.value = "Required counts nao atingido para fechar a zona."
                    dlg_required_msg.update()
                return
            dlg_required_msg.value = ""
            _set_required_styles(False)
            dlg.open = False
            page.update()
            on_refresh(None)

        open_form_dialog(
            page,
            ZONE_ADD_TITLE,
            form_column(
                [
                    dlg_event,
                    dlg_name,
                    dlg_description,
                    dlg_count_status,
                    dlg_lock_status,
                    dlg_required_msg,
                ]
            ),
            salvar_zona,
            BTN_CREATE,
            width=520,
            height=320,
        )

    coluna.controls.append(
        ft.Row(
            [
                ft.Text(ZONE_TITLE, size=28, weight=ft.FontWeight.BOLD, expand=1),
                ft.ElevatedButton(f"{ZONE_ADD}  ", icon=ICON_ADD, on_click=criar_zona),
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
                    _header_cell("Nome", expand=2),
                    _header_cell("Contagem", width=120),
                    _header_cell("Status Zona", width=120),
                    _header_cell("Evento", width=120),
                    _header_cell("Status Evento", width=120),
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

    def _build_grid_row(zona: Dict[str, Any]):
        theme = page.theme
        primary_color = (theme.color_scheme.primary if theme and theme.color_scheme else None) or ft.Colors.BLUE
        error_color = (theme.color_scheme.error if theme and theme.color_scheme else None) or ft.Colors.RED
        count_status = (zona.get("count_status") or "").lower()
        lock_status = (zona.get("lock_status") or "").lower()
        event_status = event_status_by_id.get(zona.get("event_server_id"))
        is_read_only = (
            count_status in {"finished", "locked"}
            or lock_status == "locked"
            or event_status in {"closed", "finalized"}
        )
        row = ft.Row(
            [
                _row_cell(zona.get("name") or "-", expand=2),
                _row_cell(zona.get("count_status") or "-", width=120),
                _row_cell(zona.get("lock_status") or "-", width=120),
                _row_cell(str(zona.get("event_server_id") or "-"), width=120),
                _row_cell(event_status or "-", width=120),
                ft.Container(
                    content=ft.Row(
                        [
                            action_button(
                                ICON_EDIT,
                                primary_color,
                                lambda e, zona=zona: abrir_edicao(zona),
                                disabled=is_read_only,
                            ),
                            action_button(
                                ICON_DELETE,
                                error_color,
                                lambda e, zona=zona: confirm_dialog(
                                    page,
                                    DIALOG_CONFIRM_DELETE,
                                    lambda: [service.delete(zona.get("uuid") or ""), on_refresh(None)],
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

    for zona in zonas:
        def abrir_edicao(zona=zona):
            count_status = (zona.get("count_status") or "").lower()
            lock_status = (zona.get("lock_status") or "").lower()
            event_status = event_status_by_id.get(zona.get("event_server_id"))
            if (
                count_status in {"finished", "locked"}
                or lock_status == "locked"
                or event_status in {"closed", "finalized"}
            ):
                return
            dlg_event = ft.Dropdown(
                label=FIELD_EVENT,
                options=_event_options(),
                value=str(zona.get("event_server_id") or ""),
            )
            dlg_name = ft.TextField(label=FIELD_NAME, value=zona.get("name") or "")
            dlg_description = ft.TextField(label=FIELD_DESCRIPTION, value=zona.get("description") or "")
            dlg_count_status = ft.Dropdown(
                label=f"{FIELD_STATUS} (Count)",
                options=_count_status_options(),
                value=(zona.get("count_status") or "").lower() or "not_started",
            )
            dlg_lock_status = ft.Dropdown(
                label=f"{FIELD_STATUS} (Lock)",
                options=_lock_status_options(),
                value=(zona.get("lock_status") or "").lower() or "unlocked",
            )
            disable_control(dlg_event)
            theme = page.theme
            error_color = theme.color_scheme.error if theme and theme.color_scheme else ft.Colors.RED
            dlg_required_msg = ft.Text("", color=error_color)

            def _set_required_styles(missing: bool):
                color = error_color if missing else None
                dlg_event.border_color = color
                dlg_name.border_color = color
                dlg_event.focused_border_color = color
                dlg_name.focused_border_color = color

            def salvar_edicao(e, dlg):
                result = service.update(
                    zona.get("uuid") or "",
                    dlg_event.value,
                    dlg_name.value or "",
                    dlg_description.value,
                    dlg_count_status.value,
                    dlg_lock_status.value,
                )
                if not result.ok:
                    sync_logger.info(
                        "event=ui_zone_update_failed error_code=%s message=%s uuid=%s",
                        result.error_code,
                        result.message,
                        zona.get("uuid"),
                    )
                    if result.error_code == "VALIDATION_ERROR":
                        dlg_required_msg.value = "Informacoes obrigatorias"
                        _set_required_styles(True)
                        dlg_event.update()
                        dlg_name.update()
                        dlg_required_msg.update()
                    elif result.error_code == "REQUIRED_COUNTS_NOT_MET":
                        dlg_required_msg.value = "Required counts nao atingido para fechar a zona."
                        dlg_required_msg.update()
                    elif result.error_code == "ZONE_READ_ONLY":
                        dlg_required_msg.value = "Zona fechada nao permite edicao."
                        dlg_required_msg.update()
                    return
                dlg_required_msg.value = ""
                _set_required_styles(False)
                dlg.open = False
                page.update()
                on_refresh(None)

            open_form_dialog(
                page,
                ZONE_EDIT_TITLE,
                form_column(
                    [
                        dlg_event,
                        dlg_name,
                        dlg_description,
                        dlg_count_status,
                        dlg_lock_status,
                        dlg_required_msg,
                    ]
                ),
                salvar_edicao,
                BTN_SAVE,
                width=520,
                height=320,
            )

        list_view.controls.append(_build_grid_row(zona))

    coluna.controls.append(_build_grid_header())
    coluna.controls.append(list_view)
    return coluna
