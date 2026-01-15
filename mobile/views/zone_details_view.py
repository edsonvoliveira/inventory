# mobile/views/zone_details_view.py

"""
Responsibilities:
- Render the zone details view.
- Wire UI events and interactions.
"""

import flet as ft

from core.app_state import AppState
from core.navigation import ROUTES
from core.theme import THEME, TOUCH
from data.queries import count_distinct_products_for_zone
from utils.ui import toast


def zone_details_content(page: ft.Page, state: AppState):
    zone_id = state.selected_zone
    event_id = state.selected_event

    if not (zone_id and event_id):
        toast(page, "Local, Evento ou Zona não selecionados", success=False)
        return ft.Column([ft.Text("Erro: Falta informação de Zona/Evento.")], expand=True)

    items_count = count_distinct_products_for_zone(event_id=event_id, zone_id=zone_id)
    state.items_counted = items_count

    summary_card = ft.Card(
        ft.Container(
            ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCATION_ON, size=18),
                        ft.Text("Zona Selecionada", size=16, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(state.selected_zone_name or "N/A", size=16),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCATION_CITY, size=18),
                        ft.Text("Local", size=16, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Text(state.selected_location_name or "N/A", size=16),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.EVENT, size=18),
                        ft.Text("Evento", size=16, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Text(state.selected_event_name or "N/A", size=16),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INVENTORY_2, size=18),
                        ft.Text("Itens Já Registrados", size=16, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(str(state.items_counted), size=16),
            ], spacing=6),
            padding=20,
            width=360,
            border_radius=8,
            bgcolor=THEME["bg_light"] if state.theme == "light" else THEME["bg_dark"],
        ),
        elevation=3,
        margin=8,
    )

    instructions_card = ft.Card(
        ft.Container(
            ft.Column([
                ft.Text("Instruções", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("• Use o scanner para ler códigos de barras rapidamente"),
                ft.Text("• Insira a quantidade contada para cada item"),
                ft.Text("• Os dados são salvos automaticamente após cada registro"),
                ft.Text("• Após ler o 1º produto o status do evento muda para em andamento"),
                ft.Text("• Você pode trabalhar offline - dados serão sincronizados depois"),
            ], spacing=4),
            padding=20,
            width=360,
            bgcolor="#273E5D",
            border_radius=8,
            border=ft.border.all(1, "#3399FF"),
        ),
        margin=8,
        elevation=2,
    )

    start_button = ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(ft.Icons.PLAY_ARROW), ft.Text("Iniciar Contagem")],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        height=TOUCH["button_height"],
        width=360,
        on_click=lambda e: page.go(ROUTES["counting"]),
    )

    return ft.Container(
        expand=True,
        content=ft.Row(
            controls=[
                ft.Column(
                    [summary_card, instructions_card, start_button],
                    spacing=12,
                    width=360,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )
