# desktop/tests/test.py

"""
Responsibilities:
- Test test behavior.
"""

import flet as ft

def main(page: ft.Page):
    page.window.full_screen = True
    page.update()

ft.app(target=main)
