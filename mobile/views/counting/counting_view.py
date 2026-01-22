# mobile/views/counting/counting_view.py

"""
Responsibilities:
- Render the counting view.
- Wire UI events and interactions.
"""

import flet as ft

from mobile.core.app_state import AppState
from mobile.core.navigation import ROUTES
from mobile.core.sync_service import _get_app_logger
from mobile.data.queries import (
    add_local_inventory_item,
    count_distinct_products_for_zone,
    is_event_closed,
    is_zone_closed,
    list_counted_product_ids,
    list_pending_inventory_items,
    list_products,
)
from mobile.utils.ui import toast
from mobile.utils.validators import parse_float


def counting_page_content(page: ft.Page, state: AppState):
    app_logger = _get_app_logger()
    zone_id = state.selected_zone
    event_id = state.selected_event
    zone_name = state.selected_zone_name or "Zona"
    location_name = state.selected_location_name or "Local"
    event_name = state.selected_event_name or "Evento"
    username = (state.profile or {}).get("username", "demo")

    if not zone_id or not event_id:
        toast(page, "Nenhuma zona/evento selecionada!", success=False)
        app_logger.info("event=ui_counting_open_failed reason=missing_zone_or_event")
        page.go(ROUTES["inventory"])
        return ft.Column([])

    is_read_only = is_zone_closed(zone_id) or is_event_closed(event_id)
    if is_read_only:
        toast(page, "Zona/Evento fechado. Contagem bloqueada.", success=False)
        app_logger.info("event=ui_counting_open_failed reason=read_only")
        page.go(ROUTES["zone_details"])
        return ft.Column([])

    text_item_count = ft.Text("Itens Contados: 0", size=16, weight=ft.FontWeight.BOLD)
    text_qty_count = ft.Text("Quantidade Contada: 0", size=16, weight=ft.FontWeight.BOLD)
    total_count_label = ft.Column([text_item_count, text_qty_count])

    search_box = ft.TextField(label="Buscar produto", expand=True, autofocus=True)
    scan_button = ft.IconButton(
        icon=ft.Icons.QR_CODE_SCANNER,
        icon_size=26,
        on_click=lambda e: [
            toast(page, "Scanner ainda não implementado!", success=False),
            app_logger.info("event=ui_scanner_unavailable"),
        ],
    )
    product_list = ft.ListView(expand=True, spacing=8, padding=5, auto_scroll=False)

    all_products = list_products()
    state.counted_product_ids_cache = set(
        list_counted_product_ids(event_id=event_id, zone_id=zone_id)
    )

    def update_total_count():
        num_items = count_distinct_products_for_zone(event_id=event_id, zone_id=zone_id)
        pending_items = list_pending_inventory_items(event_id=event_id, zone_id=zone_id)
        total_qty = sum(i["qty_counted"] for i in pending_items)

        text_item_count.value = f"Itens Contados: {num_items}"
        text_qty_count.value = f"Quantidade Contada: {total_qty}"
        page.update()

    def refresh_list(filter_text=""):
        product_list.controls.clear()
        filter_text = filter_text.lower()

        display_items = [
            p
            for p in all_products
            if p["id"] not in state.counted_product_ids_cache
            and (filter_text in p["name"].lower() or filter_text in p["sku"].lower())
        ]

        for p in display_items:
            product_list.controls.append(create_product_card(p))

        if not display_items:
            product_list.controls.append(
                ft.Text("Nenhum produto pendente encontrado para este filtro.", italic=True)
            )

        page.update()

    def create_product_card(product):
        def on_add_click(e):
            qty_field = ft.TextField(
                label="Quantidade", width=250, autofocus=True, keyboard_type=ft.KeyboardType.NUMBER
            )

            def close_dialog(e=None):
                page.close(dlg)

            def on_save_qty(ev):
                qty = parse_float((qty_field.value or "0").replace(",", "."))
                if qty is None or qty <= 0:
                    toast(page, "Quantidade inválida!", success=False)
                    app_logger.info("event=ui_counting_qty_invalid value=%s", qty_field.value)
                    return

                add_local_inventory_item(
                    zone_id=zone_id,
                    event_id=event_id,
                    username=username,
                    scanned_code=product["sku"],
                    product_id=product["id"],
                    qty_counted=qty,
                )
                app_logger.info(
                    "event=ui_counting_item_saved zone=%s event=%s product=%s qty=%s",
                    zone_id,
                    event_id,
                    product.get("id"),
                    qty,
                )

                state.counted_product_ids_cache.add(product["id"])

                close_dialog()
                update_total_count()
                refresh_list(search_box.value)
                toast(page, f"Salvo: {product['name']} ({qty})")

            dlg = ft.AlertDialog(
                title=ft.Text(f"Registrar: {product['name']}"),
                content=ft.Column([qty_field], tight=True),
                actions=[
                    ft.TextButton("Cancelar", on_click=close_dialog),
                    ft.ElevatedButton("Salvar", on_click=on_save_qty),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(dlg)

        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Row(
                    controls=[
                        ft.Column(
                            [
                                ft.Text(product["name"], size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"SKU: {product['sku']} • Unidade: {product['uom_inventory']}",
                                    size=12,
                                    color="#666",
                                ),
                            ],
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="Adicionar quantidade",
                            on_click=on_add_click,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
            elevation=2,
        )

    search_box.on_change = lambda e: refresh_list(search_box.value)

    update_total_count()
    refresh_list()

    return ft.Container(
        expand=True,
        content=ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    width=360,
                    spacing=12,
                    controls=[
                        ft.Column(
                            [
                                ft.Text(f"Zona: {zone_name}", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"Local: {location_name} | Evento: {event_name}", size=14
                                ),
                                total_count_label,
                            ]
                        ),
                        ft.Divider(),
                        ft.Row(controls=[search_box, scan_button], spacing=6),
                        ft.Divider(),
                        ft.Container(expand=True, content=product_list),
                    ],
                )
            ],
        ),
    )
