# desktop/views/management/profile_view.py

"""
Responsibilities:
- Render the profile view.
- Show logged-in user data.
- Allow password change via Supabase Auth endpoint.
"""

from __future__ import annotations

import os
from typing import Any

import flet as ft
import requests

from desktop.core.session_service import SessionService
from desktop.core.sync_service import _get_app_logger
from desktop.data.db.connection import get_connection


def _fetch_user_context() -> dict[str, Any]:
    conn = get_connection()
    try:
        user_id = SessionService.get_user_server_id()
        company_id = SessionService.get_company_server_id()
        user_row = None
        company_name = "n/a"

        if company_id is not None:
            row = conn.execute(
                """
                SELECT name FROM companies_local
                WHERE server_id = ? AND is_active = 1
                """,
                (company_id,),
            ).fetchone()
            if row:
                company_name = row[0]

        if user_id is not None:
            user_row = conn.execute(
                """
                SELECT name, email, role, username
                FROM users_local
                WHERE server_id = ? AND is_active = 1
                """,
                (user_id,),
            ).fetchone()

        if user_row:
            name, email, role, username = user_row
        else:
            name, email, role, username = ("n/a", "n/a", "n/a", "n/a")

        return {
            "name": name or "n/a",
            "email": email or "n/a",
            "role": role or "n/a",
            "username": username or "n/a",
            "company": company_name,
        }
    finally:
        conn.close()


def _show_snack(page: ft.Page, message: str, color: str) -> None:
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color,
        open=True,
        duration=2500,
    )
    page.update()


def render_profile_view(page: ft.Page, on_refresh):
    data = _fetch_user_context()

    password_field = ft.TextField(
        label="Digite a nova senha",
        password=True,
        can_reveal_password=True,
        width=260,
    )
    confirm_field = ft.TextField(
        label="Redigite a nova senha",
        password=True,
        can_reveal_password=True,
        width=260,
    )
    feedback = ft.Text("", color=ft.Colors.RED_400, size=12)

    def _change_password(e):
        app_logger = _get_app_logger()
        feedback.value = ""
        new_password = (password_field.value or "").strip()
        confirm_password = (confirm_field.value or "").strip()
        if not new_password or not confirm_password:
            feedback.value = "Informe e confirme a senha."
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=missing_fields")
            return
        if new_password != confirm_password:
            feedback.value = "As senhas nao conferem."
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=mismatch")
            return

        supabase_url = (os.getenv("SUPABASE_URL") or "").strip()
        supabase_key = (os.getenv("SUPABASE_ANON_KEY") or "").strip()
        jwt_token = (SessionService.get_jwt_token() or "").strip()

        if not supabase_url or not supabase_key:
            feedback.value = "SUPABASE_URL/ANON_KEY nao configurados."
            feedback.update()
            app_logger.info("event=ui_password_change_failed reason=missing_supabase_env")
            return
        if not jwt_token:
            feedback.value = "Token do utilizador nao disponivel."
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

    info = ft.Column(
        [
            ft.Text("Dados do Utilizador", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(f"Nome: {data['name']}"),
            ft.Text(f"Email: {data['email']}"),
            ft.Text(f"Utilizador: {data['username']}"),
            ft.Text(f"Role: {data['role']}"),
            ft.Text(f"Empresa: {data['company']}"),
        ],
        spacing=6,
    )

    change = ft.Column(
        [
            ft.Text("Alterar senha:", size=18, weight=ft.FontWeight.BOLD),
            password_field,
            confirm_field,
            ft.ElevatedButton("Alterar", on_click=_change_password),
            feedback,
        ],
        spacing=8,
    )

    return ft.Column(
        [info, ft.Divider(), change],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
