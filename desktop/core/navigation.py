import flet as ft

from desktop.core.strings import (
    SECTION_COMPANY,
    SECTION_CONFIG,
    SECTION_HOME,
    SECTION_LOCATION,
    SECTION_PRODUCT,
    SECTION_ROLE,
    SECTION_USER,
)

SECTIONS = [
    {"icone": ft.Icons.HOME, "nome": SECTION_HOME, "rota": "/"},
    {"icone": ft.Icons.BUSINESS, "nome": SECTION_COMPANY, "rota": "/company"},
    {"icone": ft.Icons.ADMIN_PANEL_SETTINGS, "nome": SECTION_ROLE, "rota": "/role"},
    {"icone": ft.Icons.PERSON, "nome": SECTION_USER, "rota": "/user"},
    {"icone": ft.Icons.LOCATION_ON, "nome": SECTION_LOCATION, "rota": "/location"},
    {"icone": ft.Icons.INVENTORY, "nome": SECTION_PRODUCT, "rota": "/product"},
    {"icone": ft.Icons.SETTINGS, "nome": SECTION_CONFIG, "rota": "/config"},
]
