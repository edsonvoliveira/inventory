# desktop/core/navigation.py

"""
Responsibilities:
- Core module for navigation.
- Provide shared application logic.
"""

import flet as ft

from desktop.core.strings import (
    SECTION_CONFIG,
    SECTION_DASHBOARD,
    SECTION_EVENT_TARGET,
    SECTION_INVENTORY_EVENT,
    SECTION_LOCATION,
    SECTION_PRODUCT,
    SECTION_PRODUCT_BARCODE,
    SECTION_PRODUCT_CATEGORY,
    SECTION_ZONE,
)
from desktop.views.management.dashboard_view import render_dashboard_view
from desktop.views.management.inventory_event_targets_view import render_inventory_event_targets_view
from desktop.views.management.inventory_events_view import render_inventory_events_view
from desktop.views.management.location_view import render_location_view
from desktop.views.management.product_barcode_view import render_product_barcode_view
from desktop.views.management.product_category_view import render_product_category_view
from desktop.views.management.product_view import render_product_view
from desktop.views.management.zones_view import render_zones_view
from desktop.views.settings.config_view import render_config_view


NAV_ITEMS = [
    {
        "icone": ft.Icons.DASHBOARD,
        "nome": SECTION_DASHBOARD,
        "rota": "/",
        "protected": True,
        "factory": render_dashboard_view,
    },
    {
        "icone": ft.Icons.CATEGORY,
        "nome": SECTION_PRODUCT_CATEGORY,
        "rota": "/product-categories",
        "protected": True,
        "factory": render_product_category_view,
    },
    {
        "icone": ft.Icons.INVENTORY,
        "nome": SECTION_PRODUCT,
        "rota": "/product",
        "protected": True,
        "factory": render_product_view,
    },
    {
        "icone": ft.Icons.QR_CODE_2,
        "nome": SECTION_PRODUCT_BARCODE,
        "rota": "/product-barcodes",
        "protected": True,
        "factory": render_product_barcode_view,
    },
    {
        "icone": ft.Icons.LOCATION_ON,
        "nome": SECTION_LOCATION,
        "rota": "/location",
        "protected": True,
        "factory": render_location_view,
    },
    {
        "icone": ft.Icons.EVENT,
        "nome": SECTION_INVENTORY_EVENT,
        "rota": "/inventory-events",
        "protected": True,
        "factory": render_inventory_events_view,
    },
    {
        "icone": ft.Icons.MAP,
        "nome": SECTION_ZONE,
        "rota": "/zones",
        "protected": True,
        "factory": render_zones_view,
    },
    {
        "icone": ft.Icons.GPS_FIXED,
        "nome": SECTION_EVENT_TARGET,
        "rota": "/event-targets",
        "protected": True,
        "factory": render_inventory_event_targets_view,
    },
    {
        "icone": ft.Icons.SETTINGS,
        "nome": SECTION_CONFIG,
        "rota": "/config",
        "protected": True,
        "factory": lambda page, on_refresh: render_config_view(),
    },
]
