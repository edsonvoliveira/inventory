# mobile/views/dashboard/dashboard_view.py

"""
Responsibilities:
- Render the dashboard view.
- Show sync and session status.
"""

import flet as ft
from datetime import datetime

from mobile.core.app_state import AppState
from mobile.core.sync_service import SyncService
from mobile.core.theme import THEME, TOUCH
from mobile.data.db.connection import get_connection
from mobile.data.repositories.app_meta_repo import get_meta
from mobile.utils.ui import toast


def _parse_error_code(raw: str | None) -> str:
    if not raw:
        return "unknown"
    if ":" in raw:
        return raw.split(":", 1)[0]
    return raw


def _format_ts(value: str | None) -> str:
    if not value or value == "n/a":
        return "n/a"
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo:
            dt = dt.astimezone()
        return f"Data: {dt:%d/%m/%Y} - Hora: {dt:%H:%M}"
    except ValueError:
        return value


def dashboard_content(page: ft.Page, state: AppState):
    last_pull_at = _format_ts(get_meta("last_pull_at") or "n/a")
    last_push_at = _format_ts(get_meta("last_push_at") or "n/a")
    conn = get_connection()
    user_role_db = None
    user_name_db = None
    try:
        pending = conn.execute(
            "SELECT COUNT(1) FROM outbox_local WHERE status = 'pending'"
        ).fetchone()[0]
        errors = conn.execute(
            """
            SELECT COUNT(1)
            FROM outbox_local
            WHERE status IN ('failed', 'error') OR last_error IS NOT NULL
            """
        ).fetchone()[0]
        error_rows = conn.execute(
            """
            SELECT table_name, operation, record_uuid, last_error
            FROM outbox_local
            WHERE status IN ('failed', 'error') OR last_error IS NOT NULL
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()
        user_server_id = get_meta("user_server_id")
        if user_server_id:
            role_row = conn.execute(
                "SELECT name, role FROM users_local WHERE server_id = ?",
                (user_server_id,),
            ).fetchone()
            if role_row:
                user_name_db, user_role_db = role_row
    finally:
        conn.close()

    def sync_now(e):
        try:
            SyncService().run()
            toast(page, "Sync iniciado", success=True)
            page.go(page.route)
        except Exception:
            toast(page, "Nao foi possivel iniciar o sync.", success=False)

    header = ft.Text(
        "Dashboard",
        size=22,
        color=THEME["text_on_dark"] if state.theme == "dark" else THEME["text_on_light"],
    )
    user_email = (state.profile or {}).get("email", "n/a")
    user_name = user_name_db or (state.profile or {}).get("name", "n/a")
    user_role = user_role_db or (state.profile or {}).get("role", "n/a")

    error_list = (
        ft.Column(
            [
                ft.Text(
                    f"{row[0]} {row[1]} ({row[2]}) - {_parse_error_code(row[3])}",
                    size=12,
                    color=THEME["text_secondary"],
                )
                for row in error_rows
            ],
            spacing=4,
        )
        if error_rows
        else ft.Text("Sem erros recentes.", size=12, color=THEME["text_secondary"])
    )

    status_card = ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Text(f"Utilizador: {user_name}", size=14, color=THEME["text_secondary"]),
                    ft.Text(f"Email: {user_email}", size=14, color=THEME["text_secondary"]),
                    ft.Text(f"Perfil: {user_role}", size=14, color=THEME["text_secondary"]),
                    ft.Divider(),
                    ft.Text(f"Ultimo pull: {last_pull_at}", size=14, color=THEME["text_secondary"]),
                    ft.Text(f"Ultimo push: {last_push_at}", size=14, color=THEME["text_secondary"]),
                    ft.Text(f"Outbox pendente: {pending}", size=14, color=THEME["text_secondary"]),
                    ft.Text(f"Erros de sync: {errors}", size=14, color=THEME["text_secondary"]),
                    ft.Text("Erros recentes (entidade/operacao/codigo):", size=12),
                    error_list,
                ],
                spacing=6,
            ),
            padding=14,
            width=360,
        ),
        margin=8,
        elevation=2,
    )

    return ft.Column(
        [
            header,
            status_card,
            ft.ElevatedButton(
                "Sync Now",
                on_click=sync_now,
                height=TOUCH["button_height"],
                width=360,
            ),
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
