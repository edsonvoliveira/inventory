import flet as ft
import sqlite3
import os
from datetime import datetime

from crud import (
    company_get_all, company_create, company_update, company_delete,
    role_get_all, role_create, role_update, role_delete,
    user_get_all, user_create, user_update, user_delete,
    location_get_all, location_create, location_update, location_delete,
    product_get_all, product_create, product_update, product_delete
)

DB_PATH = "inventory.db"

# ---------------- Criar Base de Dados ---------------- #
def inicializar_banco():
    criar_tabelas_sql = """
    CREATE TABLE IF NOT EXISTS Company (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        nif TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS Role (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (role_id) REFERENCES Role(id),
        FOREIGN KEY (company_id) REFERENCES Company(id)
    );
    CREATE TABLE IF NOT EXISTS Location (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        company_id INTEGER NOT NULL,
        FOREIGN KEY (company_id) REFERENCES Company(id),
        UNIQUE (name, company_id)
    );
    CREATE TABLE IF NOT EXISTS Product (
        id INTEGER PRIMARY KEY,
        sku TEXT NOT NULL UNIQUE,
        barcode TEXT UNIQUE,
        name TEXT NOT NULL,
        unit_cost REAL DEFAULT 0.0,
        unit_of_measure TEXT DEFAULT 'UN',
        last_updated TEXT,
        company_id INTEGER NOT NULL,
        FOREIGN KEY (company_id) REFERENCES Company(id)
    );
    """
    primeira_execucao = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    if primeira_execucao:
        conn.executescript(criar_tabelas_sql)
        conn.commit()
    conn.close()

inicializar_banco()

# ---------------- MAIN ---------------- #
def main(page: ft.Page):
    page.title = "Inventory"
    page.window.maximized = False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.center()

    menu_expandido = True
    rota_atual = "/"

    # ---------------- Funções ---------------- #
    def alternar_tema(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    def alternar_menu(e):
        nonlocal menu_expandido
        menu_expandido = not menu_expandido
        atualizar_menu()

    def navegar(e):
        page.go(e.control.data)

    # ---------------- Menu lateral ---------------- #
    secoes = [
        {"icone": ft.Icons.HOME, "nome": "Início", "rota": "/"},
        {"icone": ft.Icons.BUSINESS, "nome": "Empresas", "rota": "/company"},
        {"icone": ft.Icons.ADMIN_PANEL_SETTINGS, "nome": "Funções", "rota": "/role"},
        {"icone": ft.Icons.PERSON, "nome": "Usuários", "rota": "/user"},
        {"icone": ft.Icons.LOCATION_ON, "nome": "Locais", "rota": "/location"},
        {"icone": ft.Icons.INVENTORY, "nome": "Produtos", "rota": "/product"},
        {"icone": ft.Icons.SETTINGS, "nome": "Configurações", "rota": "/config"},
    ]

    lista_menu = ft.Column(expand=True, spacing=2)

    def criar_item_menu(secao):
        ativo = rota_atual == secao["rota"]
        cor_fundo = ft.Colors.BLUE_GREY_200 if ativo else None
        cor_texto = ft.Colors.BLUE_GREY_900 if ativo else ft.Colors.BLACK
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(secao["icone"], color=cor_texto),
                    ft.Text(secao["nome"], color=cor_texto) if menu_expandido else ft.Container(),
                ],
                alignment=ft.MainAxisAlignment.START if menu_expandido else ft.MainAxisAlignment.CENTER,
                spacing=10 if menu_expandido else 0,
            ),
            padding=10,
            tooltip=secao["nome"],
            on_click=navegar,
            data=secao["rota"],
            border_radius=ft.border_radius.all(6),
            ink=True,
            bgcolor=cor_fundo,
        )

    def atualizar_menu():
        lista_menu.controls.clear()
        for s in secoes:
            lista_menu.controls.append(criar_item_menu(s))
        menu_lateral.width = 220 if menu_expandido else 80
        page.update()

    menu_lateral = ft.Container(
        width=220,
        bgcolor=ft.Colors.BLUE_GREY_50,
        content=ft.Column(
            [
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.MENU,
                        tooltip="Expandir/retrair menu",
                        on_click=alternar_menu,icon_color="black"
                    ),
                    alignment=ft.alignment.center_left,
                    padding=ft.padding.only(top=10, left=10),
                ),
                ft.Divider(),
                lista_menu,
            ],
            expand=True,
            spacing=0,
        ),
    )

    atualizar_menu()

    # ---------------- Barra superior ---------------- #
    barra_superior = ft.Container(
        height=60,
        bgcolor=ft.Colors.BLUE_GREY_800,
        content=ft.Row(
            [
                ft.Text(
                    "Inventory Management System",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.HELP,
                            tooltip="Ajuda",
                            on_click=lambda e: print("Abrir ajuda"),
                            icon_color=ft.Colors.WHITE
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DARK_MODE,
                            tooltip="Alternar modo claro/escuro",
                            on_click=alternar_tema,
                            icon_color=ft.Colors.WHITE
                        ),
                        ft.IconButton(
                            icon=ft.Icons.NOTIFICATIONS,
                            tooltip="Notificações",
                            on_click=lambda e: print("Notificações clicadas"),
                            icon_color=ft.Colors.WHITE
                        ),

                        ft.CircleAvatar(
                            content=ft.Text("AC", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.BLUE_GREY_600,
                            tooltip="Perfil do usuário",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            spacing=20,
        ),
        padding=ft.padding.symmetric(horizontal=20),
    )

    # ---------------- Conteúdo central ---------------- #
    conteudo = ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(expand=True, spacing=10)
    )

    # ---------------- Função renderizar CRUD ---------------- #
    def renderizar_pagina(rota):
        coluna = ft.Column(expand=True, spacing=10)

        # ---- Início ----
        if rota == "/":
            coluna.controls.append(ft.Text("Página Inicial", size=24, weight=ft.FontWeight.BOLD))
            coluna.controls.append(ft.Text("Bem-vindo ao IMS!", size=18))

        # ---- Company ----
        elif rota == "/company":
            empresas = company_get_all()
            tf_name = ft.TextField(label="Nome")
            tf_nif = ft.TextField(label="NIF (Opcional)")

            def criar_empresa(e):
                nome = tf_name.value.strip() if tf_name.value else ""
                nif = tf_nif.value.strip() if tf_nif.value else None
                if not nome:
                    return
                company_create(nome, nif)
                tf_name.value = ""
                tf_nif.value = ""
                ao_mudar_rota(None)

            #parei aqui
            coluna.controls.append(
                ft.Row([
                    ft.Text("Empresas", size=28, weight=ft.FontWeight.BOLD, expand=1),
                    ft.ElevatedButton("Adicionar Empresa  ",icon=ft.Icons.ADD, on_click=criar_empresa)
                    ],spacing=5),
            )
            #coluna.controls.append(ft.Row([tf_name, tf_nif, ft.ElevatedButton("Criar", on_click=criar_empresa)], spacing=10))

            for emp in empresas:
                def abrir_edicao_empresa(emp=emp):
                    dlg_name = ft.TextField(label="Nome", value=emp["name"])
                    dlg_nif = ft.TextField(label="NIF (Opcional)", value=emp["nif"] or "")
                    dlg = ft.AlertDialog(
                        title=ft.Text("Editar Empresa"),
                        content=ft.Container(
                            content=ft.Column([dlg_name, dlg_nif], spacing=10),
                            width=500,
                            height=200,
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda e: [setattr(dlg, 'open', False), page.update()]),
                            ft.ElevatedButton(
                                "Salvar",
                                on_click=lambda e: [
                                    company_update(emp["id"], (dlg_name.value or "").strip(), (dlg_nif.value or "").strip() or None),
                                    setattr(dlg, 'open', False),
                                    page.update(),
                                    ao_mudar_rota(None)
                                ]
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                    page.overlay.append(dlg)
                    dlg.open = True
                    page.update()

                coluna.controls.append(
                    ft.Row([
                        ft.Container(ft.Text(f"{emp['id']} - {emp['name']} - {emp['nif'] or ''}",expand=1),width=400),
                        ft.ElevatedButton(
                            content=ft.Row([ft.Icon(name=ft.Icons.EDIT, color="GREEN"),],alignment=ft.MainAxisAlignment.SPACE_AROUND),
                            on_click=lambda e, emp=emp: abrir_edicao_empresa(emp)
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([ft.Icon(name=ft.Icons.DELETE, color="RED"),],alignment=ft.MainAxisAlignment.SPACE_AROUND), 
                            on_click=lambda e, id=emp['id']: [company_delete(id), ao_mudar_rota(None)]
                        ),
                    ], spacing=10)
                )

        # ---- Role ----
        elif rota == "/role":
            roles = role_get_all()
            tf_name = ft.TextField(label="Nome")

            def criar_role(e):
                nome = tf_name.value.strip() if tf_name.value else ""
                if not nome:
                    return
                role_create(nome)
                tf_name.value = ""
                ao_mudar_rota(None)

            coluna.controls.append(ft.Text("Funções", size=15, weight=ft.FontWeight.BOLD))
            #coluna.controls.append(ft.Row([tf_name, ft.ElevatedButton("Criar", on_click=criar_role)], spacing=10))
            coluna.controls.append(ft.Divider())

            for r in roles:
                def abrir_edicao_role(r=r):
                    dlg_name = ft.TextField(label="Nome", value=r["name"])
                    dlg = ft.AlertDialog(
                        title=ft.Text("Editar Função"),
                        content=ft.Container(
                            content=ft.Column([dlg_name], spacing=10),
                            width=500,
                            height=200,
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda e: [setattr(dlg, 'open', False), page.update()]),
                            ft.ElevatedButton(
                                "Salvar",
                                on_click=lambda e: [
                                    role_update(r["id"], (dlg_name.value or "").strip()),
                                    setattr(dlg, 'open', False),
                                    page.update(),
                                    ao_mudar_rota(None)
                                ]
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                    page.overlay.append(dlg)
                    dlg.open = True
                    page.update()

                coluna.controls.append(
                    ft.Row([
                        ft.Text(f"{r['id']} - {r['name']}"),
                        ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, r=r: abrir_edicao_role(r), bgcolor=ft.Colors.BLUE_GREY_100),
                        ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, id=r['id']: [role_delete(id), ao_mudar_rota(None)], bgcolor=ft.Colors.RED_ACCENT),
                    ], spacing=10)
                )

        # ---- User ----
        elif rota == "/user":
            usuarios = user_get_all()
            tf_email = ft.TextField(label="Email")
            tf_pass = ft.TextField(label="Senha")
            roles = role_get_all()
            companies = company_get_all()
            dd_role = ft.Dropdown(label="Função", options=[ft.dropdown.Option(str(r['id']), r['name']) for r in roles])
            dd_company = ft.Dropdown(label="Empresa", options=[ft.dropdown.Option(str(c['id']), c['name']) for c in companies])

            def criar_usuario(e):
                email = tf_email.value.strip() if tf_email.value else ""
                senha = tf_pass.value.strip() if tf_pass.value else ""
                if not email or not senha or not dd_role.value or not dd_company.value:
                    return
                user_create(email, senha, int(dd_role.value), int(dd_company.value))
                tf_email.value = ""
                tf_pass.value = ""
                ao_mudar_rota(None)

            coluna.controls.append(ft.Text("Usuários", size=15, weight=ft.FontWeight.BOLD))
            #coluna.controls.append(ft.Row([tf_email, tf_pass, dd_role, dd_company, ft.ElevatedButton("Criar", on_click=criar_usuario)], spacing=10))
            coluna.controls.append(ft.Divider())

            for u in usuarios:
                def abrir_edicao_user(u=u):
                    dlg_email = ft.TextField(label="Email", value=u["email"])
                    dlg_pass = ft.TextField(label="Senha", value=u["password_hash"])
                    dlg_role = ft.Dropdown(
                        label="Função",
                        options=[ft.dropdown.Option(str(r['id']), r['name']) for r in roles],
                        value=str(u["role_id"])
                    )
                    dlg_company = ft.Dropdown(
                        label="Empresa",
                        options=[ft.dropdown.Option(str(c['id']), c['name']) for c in companies],
                        value=str(u["company_id"])
                    )
                    dlg_active = ft.Checkbox(label="Ativo", value=bool(u["is_active"]))
                    dlg = ft.AlertDialog(
                        title=ft.Text("Editar Usuário"),
                        content=ft.Container(
                            content=ft.Column([dlg_email, dlg_pass, dlg_company, dlg_role, dlg_active], spacing=10),
                            width=500,
                            height=250,
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda e: [setattr(dlg, 'open', False), page.update()]),
                            ft.ElevatedButton(
                                "Salvar",
                                on_click=lambda e: [
                                    user_update(u["id"], (dlg_email.value or "").strip(), (dlg_pass.value or "").strip(),
                                                int(dlg_role.value or 0), int(dlg_company.value or 0),
                                                int(dlg_active.value or 0)),
                                    setattr(dlg, 'open', False),
                                    page.update(),
                                    ao_mudar_rota(None)
                                ]
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                    page.overlay.append(dlg)
                    dlg.open = True
                    page.update()

                coluna.controls.append(
                    ft.Row([
                        ft.Text(f"{u['id']} - {u['email']}"),
                        ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, u=u: abrir_edicao_user(u), bgcolor=ft.Colors.BLUE_GREY_100),
                        ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, id=u['id']: [user_delete(id), ao_mudar_rota(None)], bgcolor=ft.Colors.RED_ACCENT),
                    ], spacing=10)
                )

        # ---- Location ----
        elif rota == "/location":
            locais = location_get_all()
            tf_name = ft.TextField(label="Nome")
            companies = company_get_all()
            dd_company = ft.Dropdown(label="Empresa", options=[ft.dropdown.Option(str(c['id']), c['name']) for c in companies])

            def criar_local(e):
                nome = tf_name.value.strip() if tf_name.value else ""
                if not nome or not dd_company.value:
                    return
                location_create(nome, int(dd_company.value))
                tf_name.value = ""
                ao_mudar_rota(None)

            coluna.controls.append(ft.Text("Locais", size=15, weight=ft.FontWeight.BOLD))
            #coluna.controls.append(ft.Row([tf_name, dd_company, ft.ElevatedButton("Criar", on_click=criar_local)], spacing=10))
            coluna.controls.append(ft.Divider())

            for l in locais:
                def abrir_edicao_location(l=l):
                    dlg_name = ft.TextField(label="Nome", value=l["name"])
                    dlg_company = ft.Dropdown(
                        label="Empresa",
                        options=[ft.dropdown.Option(str(c['id']), c['name']) for c in companies],
                        value=str(l["company_id"])
                    )
                    dlg = ft.AlertDialog(
                        title=ft.Text("Editar Local"),
                        content=ft.Container(
                            content=ft.Column([dlg_name, dlg_company], spacing=10),
                            width=500,
                            height=250,
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda e: [setattr(dlg, 'open', False), page.update()]),
                            ft.ElevatedButton(
                                "Salvar",
                                on_click=lambda e: [
                                    location_update(l["id"], (dlg_name.value or "").strip(), int(dlg_company.value or 0)),
                                    setattr(dlg, 'open', False),
                                    page.update(),
                                    ao_mudar_rota(None)
                                ]
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                    page.overlay.append(dlg)
                    dlg.open = True
                    page.update()

                coluna.controls.append(
                    ft.Row([
                        ft.Text(f"{l['id']} - {l['name']}"),
                        ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, l=l: abrir_edicao_location(l), bgcolor=ft.Colors.BLUE_GREY_100),
                        ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, id=l['id']: [location_delete(id), ao_mudar_rota(None)], bgcolor=ft.Colors.RED_ACCENT),
                    ], spacing=10)
                )

        # ---- Product ----
        elif rota == "/product":
            produtos = product_get_all()
            tf_sku = ft.TextField(label="SKU")
            tf_barcode = ft.TextField(label="Barcode")
            tf_name = ft.TextField(label="Nome")
            tf_unit_cost = ft.TextField(label="Preço")
            tf_unit_of_measure = ft.TextField(label="Unidade")
            companies = company_get_all()
            dd_company = ft.Dropdown(label="Empresa", options=[ft.dropdown.Option(str(c['id']), c['name']) for c in companies])

            def criar_produto(e):
                sku = tf_sku.value.strip() if tf_sku.value else ""
                name = tf_name.value.strip() if tf_name.value else ""
                barcode = tf_barcode.value.strip() if tf_barcode.value else ""
                unit_cost = float(tf_unit_cost.value or 0)
                unit_of_measure = tf_unit_of_measure.value.strip() if tf_unit_of_measure.value else "UN"
                if not sku or not name or not dd_company.value:
                    return
                product_create(sku, barcode, name, unit_cost, unit_of_measure, datetime.now().isoformat(), int(dd_company.value))
                tf_sku.value = ""
                tf_name.value = ""
                tf_barcode.value = ""
                tf_unit_cost.value = ""
                tf_unit_of_measure.value = ""
                ao_mudar_rota(None)

            coluna.controls.append(ft.Text("Produtos", size=15, weight=ft.FontWeight.BOLD))
            #coluna.controls.append(ft.Row([tf_sku, tf_barcode, tf_name, tf_unit_cost, tf_unit_of_measure, dd_company, ft.ElevatedButton("Criar", on_click=criar_produto)], spacing=10))
            coluna.controls.append(ft.Divider())

            for p in produtos:
                def abrir_edicao_product(p=p):
                    dlg_sku = ft.TextField(label="SKU", value=p["sku"])
                    dlg_barcode = ft.TextField(label="Barcode", value=p["barcode"] or "")
                    dlg_name = ft.TextField(label="Nome", value=p["name"])
                    dlg_unit_cost = ft.TextField(label="Preço", value=str(p["unit_cost"]))
                    dlg_unit_of_measure = ft.TextField(label="Unidade", value=p["unit_of_measure"])
                    dlg_company = ft.Dropdown(
                        label="Empresa",
                        options=[ft.dropdown.Option(str(c['id']), c['name']) for c in companies],
                        value=str(p["company_id"])
                    )
                    dlg = ft.AlertDialog(
                        title=ft.Text("Editar Produto"),
                        content=ft.Container(
                            content=ft.Column([dlg_sku, dlg_barcode, dlg_name, dlg_unit_cost, dlg_unit_of_measure, dlg_company], spacing=10),
                            width=500,
                            height=250,
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda e: [setattr(dlg, 'open', False), page.update()]),
                            ft.ElevatedButton(
                                "Salvar",
                                on_click=lambda e: [
                                    product_update(p["id"], (dlg_sku.value or "").strip(), (dlg_barcode.value or "").strip(), (dlg_name.value or "").strip(),
                                                   float(dlg_unit_cost.value or 0), (dlg_unit_of_measure.value or "").strip(),
                                                   datetime.now().isoformat(), int(dlg_company.value or 0)),
                                    setattr(dlg, 'open', False),
                                    page.update(),
                                    ao_mudar_rota(None)
                                ]
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                    page.overlay.append(dlg)
                    dlg.open = True
                    page.update()

                coluna.controls.append(
                    ft.Row([
                        ft.Text(f"{p['id']} - {p['sku']} - {p['name']}"),
                        ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, p=p: abrir_edicao_product(p), bgcolor=ft.Colors.GREEN_ACCENT_100),
                        ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, id=p['id']: [product_delete(id), ao_mudar_rota(None)], bgcolor=ft.Colors.RED_ACCENT),
                    ], spacing=10)
                )

        # ---- Configurações ----
        elif rota == "/config":
            coluna.controls.append(ft.Text("⚙️ Configurações", size=24, weight=ft.FontWeight.BOLD))
            coluna.controls.append(ft.Text("Preferências e ajustes do sistema."))

        return coluna

    # ---------------- Atualizar rota ---------------- #
    def ao_mudar_rota(e):
        nonlocal rota_atual
        rota_atual = page.route
        atualizar_menu()  # Mantém menu atualizado

        nova_coluna = renderizar_pagina(page.route)
        if isinstance(conteudo.content, ft.Column):
            conteudo.content.controls.clear()
            if isinstance(nova_coluna, ft.Column):
                conteudo.content.controls.extend(nova_coluna.controls)
            else:
                conteudo.content.controls.append(nova_coluna)
        page.update()

    page.on_route_change = ao_mudar_rota

    # ---------------- Layout principal ---------------- #
    layout = ft.Column(
        [
            barra_superior,
            ft.Row(
                [menu_lateral, conteudo],
                expand=True,
            ),
        ],
        expand=True,
    )

    page.add(layout)
    page.go(page.route or "/")

if __name__ == "__main__":
    ft.app(target=main)
