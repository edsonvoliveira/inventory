# mobile/views/profile_view.py

"""
Responsibilities:
- Render the profile view.
- Wire UI events and interactions.
"""

import flet as ft

from mobile.core.app_state import AppState
from mobile.core.auth_service import AuthService
from mobile.core.navigation import ROUTES
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


def profile_content(page: ft.Page, state: AppState):
    auth_service = AuthService()
    prof = state.profile or {}
    last_pull_at = get_meta("last_pull_at") or "n/a"
    conn = get_connection()
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
    finally:
        conn.close()
    user_card = ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON, size=48),
                            ft.Text(prof.get("username", "Demo"), size=20),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=12,
                    ),
                    ft.Text(prof.get("email", "demo@example.com"), size=16, color=THEME["text_secondary"]),
                    ft.Text(f"Perfil: {prof.get('role', 'Usuario')}", size=16, color=THEME["text_secondary"]),
                ],
                spacing=8,
            ),
            padding=12,
        ),
        margin=10,
        elevation=2,
    )
    action_card = ft.Container(
        ft.Column(
            [
                ft.ElevatedButton(
                    "Alterar senha",
                    on_click=lambda e: toast(page, "Alterar senha"),
                    height=TOUCH["button_height"],
                ),
                ft.ElevatedButton(
                    "Sair",
                    on_click=lambda e: _handle_logout(e, page, state, auth_service),
                    height=TOUCH["button_height"],
                    bgcolor=THEME["danger"],
                    color="white",
                ),
            ],
            spacing=12,
        ),
        padding=12,
    )

    info_card = ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Text("Sistema de Inventário Mobile", size=16),
                    ft.Text("Versão 1.0.0", size=14, color=THEME["text_secondary"]),
                ],
                spacing=4,
            ),
            padding=12,
        ),
        margin=10,
        elevation=2,
    )

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

    sync_card = ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Text("Status de Sync", size=16),
                    ft.Text(f"Ultimo pull: {last_pull_at}", size=14, color=THEME["text_secondary"]),
                    ft.Text(f"Outbox pendente: {pending}", size=14, color=THEME["text_secondary"]),
                    ft.Text(f"Erros de sync: {errors}", size=14, color=THEME["text_secondary"]),
                    ft.Text("Erros recentes (entidade/operacao/codigo):", size=12),
                    error_list,
                ],
                spacing=4,
            ),
            padding=12,
        ),
        margin=10,
        elevation=2,
    )

    return ft.Column(
        [user_card, action_card, sync_card, info_card],
        spacing=12,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _handle_logout(e, page: ft.Page, state: AppState, auth_service: AuthService) -> None:
    result = auth_service.logout()
    if not result.ok:
        toast(page, "Nao foi possivel sair agora. Tente novamente.", success=False)
        return
    state.clear_session()
    if state.sync_scheduler is not None:
        state.sync_scheduler.stop()
        state.sync_scheduler = None
    toast(page, "Sessao encerrada.", success=True)
    page.go(ROUTES["login"])
