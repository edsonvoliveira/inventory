# main_factory.py
import flet as ft
from db import (
    init_db, save_local_profile, get_local_profile,
    list_locations, list_events_for_location, list_zones_for_event
)
from ui_helpers import THEME, TOUCH

# ----------------------
# App state
# ----------------------
APP = {
    "profile": None,
    "selected_location": None,
    "selected_event": None,
    "selected_zone": None,
    "scanner": None,
    "scanning": False,
    "theme": "dark"
}

# ----------------------
# Helpers
# ----------------------
def apply_theme(page: ft.Page):
    if APP["theme"] == "dark":
        page.bgcolor = THEME["bg_dark"]
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.bgcolor = THEME["bg_light"]
        page.theme_mode = ft.ThemeMode.LIGHT
    page.update()

def toggle_theme(page: ft.Page):
    APP["theme"] = "light" if APP["theme"]=="dark" else "dark"
    apply_theme(page)

def toast(page: ft.Page, text: str, success=True):
    color = THEME["success"] if success else THEME["danger"]
    snack = ft.SnackBar(content=ft.Text(text), bgcolor=color, open=True, duration=2000)
    page.overlay.append(snack)
    page.update()

# ----------------------
# Layout Base
# ----------------------
class ScreenBase:
    """Tela base com AppBar e FooterBar."""
    def __init__(self, page: ft.Page, main_content: ft.Control, show_footer=True):
        self.page = page
        self.main_content = main_content
        self.show_footer = show_footer
        self.view = ft.View()

    def build_appbar(self):
        return ft.Container(
            ft.Row([
                ft.Text("Inventory Mobile"),
                ft.IconButton(ft.Icons.DARK_MODE, on_click=lambda e: toggle_theme(self.page)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            height=56,
            bgcolor=THEME["bg_dark"]
        )

    def build_footer(self):
        return ft.Container(
            ft.Row([
                ft.IconButton(ft.Icons.HOME, on_click=lambda e: self.page.go("/dashboard")),
                ft.IconButton(ft.Icons.PERSON, on_click=lambda e: self.page.go("/profile"))
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            height=56,
            bgcolor=THEME["bg_dark"]
        )

    def show(self):
        controls = [self.build_appbar(), self.main_content]
        if self.show_footer:
            controls.append(self.build_footer())
        self.view.controls.clear()
        self.view.controls.append(ft.SafeArea(ft.Column(controls, expand=True), expand=True))
        self.page.views.clear()
        self.page.views.append(self.view)
        self.page.update()

# ----------------------
# Fábrica de Telas
# ----------------------
class ScreenFactory:
    """Gerencia telas sem blink, com AppBar/Footer fixos."""
    def __init__(self, page: ft.Page, show_footer=True):
        self.page = page
        self.show_footer = show_footer

        # Containers fixos
        self.appbar = self.build_appbar()
        self.main_container = ft.Column(expand=True)  # conteúdo que muda
        self.footer = self.build_footer() if self.show_footer else None

        # View única
        self.view = ft.View()
        controls = [self.appbar, self.main_container]
        if self.footer:
            controls.append(self.footer)
        self.view.controls.append(ft.SafeArea(ft.Column(controls, expand=True), expand=True))

        self.page.views.append(self.view)
        self.registry = {}

    def build_appbar(self):
        return ft.Container(
            ft.Row([
                ft.Text("Inventory Mobile"),
                ft.IconButton(ft.Icons.BRIGHTNESS_6, on_click=lambda e: toggle_theme(self.page)),
                # ft.IconButton(ft.Icons.PERSON, on_click=lambda e: self.page.go("/profile"))  # removido
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            height=56,
            bgcolor=THEME["bg_dark"]
        )

    def build_footer(self):
        return ft.Container(
            ft.Row([
                ft.IconButton(ft.Icons.HOME, on_click=lambda e: self.show("/dashboard")),
                ft.IconButton(ft.Icons.PERSON, on_click=lambda e: self.show("/profile"))
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            height=56,
            bgcolor=THEME["bg_dark"]
        )

    def register(self, route: str, content_builder):
        self.registry[route] = content_builder

    def show(self, route: str):
        builder = self.registry.get(route)
        if builder:
            # Atualiza apenas o conteúdo principal
            self.main_container.controls.clear()
            self.main_container.controls.append(builder(self.page))
            self.page.update()
        else:
            self.page.go("/login")



# ----------------------
# Telas
# ----------------------
def login_content(page: ft.Page):
    username_field = ft.TextField(label="Usuário", width=400, height=TOUCH["input_height"])
    password_field = ft.TextField(label="Senha", width=400, height=TOUCH["input_height"], password=True)

    def on_login(e):
        username = (username_field.value or "").strip()
        password = (password_field.value or "").strip()
        if username == "admin" and password == "1234":
            try:
                save_local_profile(username=username, password=password)
                APP["profile"] = get_local_profile()
                toast(page, "Login bem-sucedido", success=True)
                page.go("/dashboard")
            except Exception as ex:
                toast(page, f"Erro ao salvar perfil: {ex}", success=False)
        else:
            toast(page, "Usuário ou senha incorretos", success=False)

    return ft.Column([
        ft.Text("Entrar", size=24, color=THEME["text_on_dark"] if APP["theme"]=="dark" else THEME["text_on_light"]),
        username_field,
        password_field,
        ft.ElevatedButton("Entrar", on_click=on_login, height=TOUCH["button_height"])
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

def dashboard_content(page: ft.Page):
    locs = list_locations()
    location_dd = ft.Dropdown(label="Local", width=420, options=[ft.dropdown.Option(str(l["id"]), l["name"]) for l in locs])
    event_dd = ft.Dropdown(label="Evento", width=420, options=[])
    zones_list = ft.ListView(expand=True, spacing=8, padding=10)

    def on_location_change(e):
        if not location_dd.value:
            return
        APP["selected_location"] = int(location_dd.value)
        evs = list_events_for_location(int(location_dd.value))
        event_dd.options = [ft.dropdown.Option(str(ev["id"]), ev["title"]) for ev in evs]
        page.update()

    def on_event_change(e):
        if not event_dd.value:
            return
        APP["selected_event"] = int(event_dd.value)
        zones = list_zones_for_event(int(event_dd.value))
        zones_list.controls.clear()
        for z in zones:
            btn = ft.ElevatedButton("Começar a Contagem", on_click=lambda evt, zid=z["id"]: toast(page, f"Start zone {zid}"), height=40)
            zones_list.controls.append(ft.Card(ft.ListTile(title=ft.Text(z["name"]), subtitle=ft.Text(f"Zone ID: {z['id']}"), trailing=btn)))
        page.update()

    location_dd.on_change = on_location_change
    event_dd.on_change = on_event_change

    return ft.Column([
        ft.Text("Dashboard de Tarefa", size=22, color=THEME["text_on_dark"] if APP["theme"]=="dark" else THEME["text_on_light"]),
        location_dd,
        event_dd,
        ft.Text("Zonas", color=THEME["text_on_dark"] if APP["theme"]=="dark" else THEME["text_on_light"]),
        zones_list,
        ft.ElevatedButton("Transações Pendentes", on_click=lambda e: toast(page, "Pending clicked"), height=TOUCH["button_height"])
    ], spacing=12, expand=True)

def profile_content(page: ft.Page):
    user_card = ft.Card(
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=48),
                    ft.Text(APP['profile'].get('username', 'Demo'), size=20),
                ], alignment=ft.MainAxisAlignment.START, spacing=12),
                ft.Text(APP['profile'].get('email', 'demo@example.com'), size=16, color=THEME["text_secondary"]),
                ft.Text(f"Perfil: {APP['profile'].get('role', 'Usuario')}", size=16, color=THEME["text_secondary"]),
            ], spacing=8),
        padding=12),
        margin=10,
        elevation=2
    )
    action_card = ft.Container(
        ft.Column([
            ft.Row([
                ft.ElevatedButton("Alterar senha", on_click=lambda e: toast(page, "Alterar senha"), height=TOUCH["button_height"]),
            ], spacing=12),
            ft.Row([
                ft.ElevatedButton("Sair", on_click=lambda e: page.go("/login"), height=TOUCH["button_height"], bgcolor=THEME["danger"], color="white")
            ], spacing=12)
        ], spacing=8),
    padding=12)

    info_card = ft.Card(
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Text("Sistema de Inventário Mobile", size=16),
                ], alignment=ft.MainAxisAlignment.START, spacing=4),
                ft.Row([
                    ft.Text("Versão 1.0.0", size=14, color=THEME["text_secondary"])
                ], alignment=ft.MainAxisAlignment.START, spacing=4),
            ], spacing=4),
            
        padding=12),
        margin=10,
        elevation=2
    )

    return ft.Column([user_card, action_card, info_card], spacing=12, expand=True)


# ----------------------
# Main
# ----------------------
def main(page: ft.Page):
    page.title = "Inventory Mobile"
    init_db()
    APP["profile"] = get_local_profile()
    apply_theme(page)

    factory = ScreenFactory(page)
    # Registro das telas
    factory.register("/login", login_content)
    factory.register("/dashboard", dashboard_content)
    factory.register("/profile", profile_content)

    page.on_route_change = lambda e: factory.show(e.route)

    # Navegação inicial
    if APP["profile"]:
        page.go("/dashboard")
    else:
        page.go("/login")

    page.update()

# ----------------------
# Run app
# ----------------------
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
