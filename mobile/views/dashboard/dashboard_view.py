# mobile/views/dashboard/dashboard_view.py

"""
Responsibilities:
- Render the dashboard view.
- Wire UI events and interactions.
"""

import flet as ft

from mobile.core.app_state import AppState
from mobile.core.navigation import ROUTES
from mobile.core.theme import THEME
from mobile.data.queries import list_events_for_location, list_locations, list_zones_for_event
from mobile.utils.ui import get_option_label


def dashboard_content(page: ft.Page, state: AppState):
    state.selected_location = None
    state.selected_event = None
    state.selected_zone = None
    state.counted_product_ids_cache.clear()

    locs = list_locations()
    location_dd = ft.Dropdown(
        label="Local", width=360, options=[ft.dropdown.Option(str(l["id"]), l["name"]) for l in locs]
    )
    event_dd = ft.Dropdown(label="Evento", width=360, options=[])
    zones_header = ft.Text(
        "Zonas Disponíveis",
        color=THEME["text_on_dark"] if state.theme == "dark" else THEME["text_on_light"],
    )
    zones_list = ft.ListView(expand=True, spacing=8, padding=10)
    main_column = None

    def build_event_dropdown(options):
        return ft.Dropdown(
            label="Evento",
            width=360,
            options=options,
            on_change=on_event_change,
        )

    def on_location_change(e):
        nonlocal event_dd, main_column
        event_dd.value = None
        event_dd.options.clear()
        zones_list.controls.clear()
        zones_header.value = "Zonas Disponiveis"

        if not location_dd.value:
            page.update()
            return

        loc_id = int(location_dd.value)
        state.selected_location = loc_id
        state.selected_event = None
        state.selected_zone = None

        evs = list_events_for_location(loc_id)
        new_options = [ft.dropdown.Option(str(ev["id"]), ev["title"]) for ev in evs]
        event_dd = build_event_dropdown(new_options)
        if main_column is not None:
            main_column.controls[2] = event_dd
        page.update()

    def on_event_change(e):
        if not e.control.value:
            zones_list.controls.clear()
            zones_header.value = "Zonas Disponiveis"
            page.update()
            return

        evt_id = int(e.control.value)
        state.selected_event = evt_id
        state.selected_zone = None

        zones = list_zones_for_event(evt_id)
        zones_list.controls.clear()

        def on_zone_select(zid, zname):
            state.selected_zone = zid
            state.selected_zone_name = zname
            state.selected_location_name = get_option_label(location_dd)
            state.selected_event_name = get_option_label(e.control)
            page.go(ROUTES["zone_details"])

        for z in zones:
            zid = z["id"]
            zname = z["name"]

            card = ft.GestureDetector(
                on_tap=lambda e, zid=zid, zname=zname: on_zone_select(zid, zname),
                content=ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(zname, size=18),
                            ft.Text(f"Zone ID: {zid}", size=12, color=THEME["text_secondary"]),
                        ]),
                        padding=10,
                    ),
                    elevation=3,
                    margin=5,
                ),
            )
            zones_list.controls.append(card)

        zones_header.value = f"Zonas Disponiveis ({len(zones)})"
        page.update()

    location_dd.on_change = on_location_change
    event_dd.on_change = on_event_change
    zones_list.controls.clear()

    main_column = ft.Column(
        [
            ft.Text(
                "Dashboard de Tarefa",
                size=22,
                color=THEME["text_on_dark"] if state.theme == "dark" else THEME["text_on_light"],
            ),
            location_dd,
            event_dd,
            zones_header,
            zones_list,
        ],
        spacing=12,
        width=360,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return main_column
