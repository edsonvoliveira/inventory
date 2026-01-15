import flet as ft

from core.app_state import AppState
from core.navigation import ROUTES
from core.theme import THEME, TOUCH
from data.queries import get_local_profile, save_local_profile
from utils.ui import toast


def login_content(page: ft.Page, state: AppState):
    username_field = ft.TextField(label="Usuário", width=360, height=TOUCH["input_height"])
    password_field = ft.TextField(
        label="Senha", width=360, height=TOUCH["input_height"], password=True
    )

    def on_login(e):
        username = (username_field.value or "").strip()
        password = (password_field.value or "").strip()
        if username == "admin" and password == "1234":
            try:
                save_local_profile(username=username, password=password)
                state.profile = get_local_profile()
                toast(page, "Login bem-sucedido", success=True)
                page.go(ROUTES["dashboard"])
            except Exception as ex:
                toast(page, f"Erro ao salvar perfil: {ex}", success=False)
        else:
            toast(page, "Usuário ou senha incorretos", success=False)

    return ft.Column(
        [
            ft.Text(
                "Entrar",
                size=24,
                color=THEME["text_on_dark"] if state.theme == "dark" else THEME["text_on_light"],
            ),
            username_field,
            password_field,
            ft.ElevatedButton("Entrar", on_click=on_login, height=TOUCH["button_height"]),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
