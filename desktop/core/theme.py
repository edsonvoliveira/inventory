# desktop/core/theme.py

"""
Responsibilities:
- Core module for theme.
- Provide shared application logic.
"""

from dataclasses import dataclass

import flet as ft


@dataclass(frozen=True)
class ThemeTokens:
    bg: str
    surface: str
    surface_alt: str
    text: str
    text_muted: str
    primary: str
    primary_dark: str
    accent: str
    menu_bg: str
    menu_active_bg: str
    menu_text: str
    menu_text_muted: str
    topbar_bg: str
    topbar_text: str
    border: str
    success: str
    danger: str


def get_theme_tokens(mode: ft.ThemeMode | None) -> ThemeTokens:
    if mode == ft.ThemeMode.DARK:
        return ThemeTokens(
            bg="#0E1110",
            surface="#151917",
            surface_alt="#1C211F",
            text="#E8EFEA",
            text_muted="#A3B3A8",
            primary="#22C1A6",
            primary_dark="#119E88",
            accent="#E2B04A",
            menu_bg="#141A17",
            menu_active_bg="#203129",
            menu_text="#E8EFEA",
            menu_text_muted="#9FB0A6",
            topbar_bg="#0F1714",
            topbar_text="#E8EFEA",
            border="#27302C",
            success="#5AD1A2",
            danger="#F0756A",
        )
    return ThemeTokens(
        bg="#F7F7F4",
        surface="#FFFFFF",
        surface_alt="#F1F3F2",
        text="#1C2420",
        text_muted="#6A7A71",
        primary="#0F766E",
        primary_dark="#0B5F59",
        accent="#C48B2C",
        menu_bg="#EEF1EF",
        menu_active_bg="#D9E5E0",
        menu_text="#1C2420",
        menu_text_muted="#5C6B63",
        topbar_bg="#163A2D",
        topbar_text="#F2F7F4",
        border="#D7DED9",
        success="#2E9B6F",
        danger="#D24C3F",
    )


def build_theme(tokens: ThemeTokens) -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=tokens.primary,
        font_family="Avenir Next",
        use_material3=True,
    )
