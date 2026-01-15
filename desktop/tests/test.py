import flet as ft

def main(page: ft.Page):
    page.window.full_screen = True
    page.update()

ft.app(target=main)
