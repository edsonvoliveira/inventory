# mobile/views/profile_view.py

"""
Responsibilities:
- Render the profile view.
- Wire UI events and interactions.
"""

import os

import flet as ft
import requests

from mobile.core.app_state import AppState
from mobile.core.auth_service import AuthService
from mobile.core.navigation import ROUTES
from mobile.core.theme import THEME, TOUCH
from mobile.core.sync_service import SyncService, _get_app_logger
from mobile.data.db.connection import get_connection
from mobile.data.repositories.app_meta_repo import get_meta
from mobile.utils.ui import toast


def profile_content(page: ft.Page, state: AppState):
    auth_service = AuthService()
    prof = state.profile or {}
    user_server_id = get_meta("user_server_id")
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT uuid, server_id, company_server_id, name, role, is_active, updated_at
            FROM users_local
            WHERE server_id = ?
            """,
            (user_server_id,),
        ).fetchone()
    finally:
        conn.close()
    user = {
        "uuid": row[0] if row else None,
        "server_id": row[1] if row else None,
        "company_server_id": row[2] if row else None,
        "name": row[3] if row else None,
        "role": row[4] if row else None,
        "is_active": row[5] if row else None,
        "updated_at": row[6] if row else None,
    }
    display_name = user["name"] or prof.get("name") or prof.get("username") or "Utilizador"
    display_role = user["role"] or prof.get("role") or "Usuario"
    display_email = prof.get("email") or "n/a"
    display_username = prof.get("username") or "n/a"
    initials = "".join([part[:1].upper() for part in display_name.split()[:2]]).strip() or "U"
    user_card = ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.CircleAvatar(
                                content=ft.Text(initials, color="white"),
                                bgcolor=THEME["primary"],
                                radius=28,
                            ),
                            ft.Column(
                                [
                                    ft.Text(display_name, size=20),
                                    ft.Text(display_email, size=14, color=THEME["text_secondary"]),
                                ],
                                spacing=2,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=12,
                    ),
                    ft.Text(f"Perfil: {display_role}", size=16, color=THEME["text_secondary"]),
                    ft.Text(
                        f"Ativo: {'Sim' if user['is_active'] == 1 else 'Nao'}",
                        size=14,
                        color=THEME["text_secondary"],
                    ),
                    ft.Text(
                        f"ID servidor: {user['server_id'] or 'n/a'}",
                        size=14,
                        color=THEME["text_secondary"],
                    ),
                    ft.Text(
                        f"Empresa (ID): {user['company_server_id'] or 'n/a'}",
                        size=14,
                        color=THEME["text_secondary"],
                    ),
                    ft.Text(
                        f"Utilizador: {display_username}",
                        size=14,
                        color=THEME["text_secondary"],
                    ),
                    ft.ElevatedButton(
                        "Sair",
                        on_click=lambda e: _handle_logout(e, page, state, auth_service),
                        height=TOUCH["button_height"],
                        bgcolor=THEME["danger"],
                        color="white",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=22),
                        ),
                    ),
                ],
                spacing=8,
            ),
            padding=12,
        ),
        margin=10,
        elevation=2,
    )

    password_field = ft.TextField(
        label="Digite a nova senha",
        password=True,
        can_reveal_password=True,
        width=320,
        height=TOUCH["input_height"],
    )
    confirm_field = ft.TextField(
        label="Redigite a nova senha",
        password=True,
        can_reveal_password=True,
        width=320,
        height=TOUCH["input_height"],
    )
    feedback = ft.Text("", color=ft.Colors.RED_400, size=12)

    def _change_password(e):
        app_logger = _get_app_logger()
        feedback.value = ""
        new_password = (password_field.value or "").strip()
        confirm_password = (confirm_field.value or "").strip()
        if not new_password or not confirm_password:
            feedback.value = "Informe e confirme a senha."
            feedback.color = ft.Colors.RED_400
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=missing_fields")
            return
        if new_password != confirm_password:
            feedback.value = "As senhas nao conferem."
            feedback.color = ft.Colors.RED_400
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=mismatch")
            return

        supabase_url = (os.getenv("SUPABASE_URL") or "").strip()
        supabase_key = (os.getenv("SUPABASE_ANON_KEY") or "").strip()
        jwt_token = (get_meta("jwt_token") or "").strip()
        if not supabase_url or not supabase_key:
            feedback.value = "SUPABASE_URL/ANON_KEY nao configurados."
            feedback.color = ft.Colors.RED_400
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=missing_supabase_env")
            return
        if not jwt_token:
            feedback.value = "Token do utilizador nao disponivel."
            feedback.color = ft.Colors.RED_400
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=missing_token")
            return

        url = f"{supabase_url.rstrip('/')}/auth/v1/user"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "apikey": supabase_key,
            "Content-Type": "application/json",
        }
        try:
            resp = requests.put(url, json={"password": new_password}, headers=headers, timeout=10)
        except requests.RequestException:
            feedback.value = "Erro ao comunicar com o Supabase."
            feedback.color = ft.Colors.RED_400
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=request_error")
            return

        if resp.ok:
            password_field.value = ""
            confirm_field.value = ""
            password_field.update()
            confirm_field.update()
            feedback.color = ft.Colors.GREEN_400
            feedback.value = "Senha alterada com sucesso."
            feedback.update()
            app_logger.info("event=ui_password_change_success")
            return

        try:
            payload = resp.json()
            error = payload.get("error_description") or payload.get("msg") or payload.get("message")
        except ValueError:
            error = None
        feedback.color = ft.Colors.RED_400
        feedback.value = error or "Nao foi possivel alterar a senha."
        feedback.update()
        app_logger.info("event=ui_password_change_failed reason=api_error status=%s", resp.status_code)

    password_card = ft.Container(
        ft.Column(
            [
                ft.Text("Alterar senha:", size=16),
                password_field,
                confirm_field,
                ft.ElevatedButton(
                    "Alterar",
                    on_click=_change_password,
                    height=TOUCH["button_height"],
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=22),
                    ),
                ),
                feedback,
            ],
            spacing=8,
        ),
        padding=12,
    )

    return ft.Column(
        [user_card, ft.Divider(), password_card],
        spacing=12,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _handle_logout(e, page: ft.Page, state: AppState, auth_service: AuthService) -> None:
    app_logger = _get_app_logger()
    try:
        SyncService().run()
        app_logger.info("event=ui_logout_forced_sync")
    except Exception:
        app_logger.info("event=ui_logout_forced_sync_failed")
    state.clear_session()
    if state.sync_scheduler is not None:
        state.sync_scheduler.stop()
        state.sync_scheduler = None
    result = auth_service.logout()
    if not result.ok:
        toast(page, "Nao foi possivel sair agora. Tente novamente.", success=False)
        app_logger.info("event=ui_logout_failed")
        return
    toast(page, "Sessao encerrada.", success=True)
    app_logger.info("event=ui_logout_success")
    page.go(ROUTES["login"])
