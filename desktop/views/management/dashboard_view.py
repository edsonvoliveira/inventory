# desktop/views/management/dashboard_view.py

"""
Responsibilities:
- Render the dashboard view.
- Provide read-only status indicators.
"""

import flet as ft

from desktop.core.session_service import SessionService
from desktop.core.sync_service import SyncService
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import get_meta


def _status_dot(ok: bool) -> ft.Container:
    color = ft.Colors.GREEN_400 if ok else ft.Colors.RED_400
    return ft.Container(width=10, height=10, bgcolor=color, border_radius=10)


def _fetch_context():
    conn = get_connection()
    try:
        company_server_id = SessionService.get_company_server_id()
        user_server_id = SessionService.get_user_server_id()
        company_name = "n/a"
        user_email = "n/a"
        user_role = "n/a"

        if company_server_id is not None:
            row = conn.execute(
                """
                SELECT name FROM companies_local
                WHERE server_id = ? AND deleted_at IS NULL
                """,
                (company_server_id,),
            ).fetchone()
            if row:
                company_name = row[0]

        if user_server_id is not None:
            row = conn.execute(
                """
                SELECT email, role FROM users_local
                WHERE server_id = ? AND deleted_at IS NULL
                """,
                (user_server_id,),
            ).fetchone()
            if row:
                user_email = row[0]
                user_role = row[1]

        last_pull = get_meta("last_pull_at", conn) or "n/a"
        last_bootstrap = last_pull if get_meta("bootstrap_done", conn) in {"1", "true"} else "n/a"
        last_push = get_meta("last_push_at", conn) or "n/a"

        pending = conn.execute(
            "SELECT COUNT(1) FROM outbox_local WHERE status = 'pending'"
        ).fetchone()[0]
        sync_errors = conn.execute(
            "SELECT COUNT(1) FROM outbox_local WHERE status = 'failed' OR last_error IS NOT NULL"
        ).fetchone()[0]
        zones_blocked = conn.execute(
            """
            SELECT COUNT(1) FROM zones_local
            WHERE lock_status IS NOT NULL AND lock_status != '' AND lock_status != 'unlocked'
            """
        ).fetchone()[0]
        events_delayed = conn.execute(
            """
            SELECT COUNT(1) FROM inventory_events_local
            WHERE status IN ('delayed', 'overdue')
            """
        ).fetchone()[0]

        return {
            "company_name": company_name,
            "user_email": user_email,
            "user_role": user_role,
            "last_bootstrap": last_bootstrap,
            "last_pull": last_pull,
            "last_push": last_push,
            "pending": pending,
            "sync_errors": sync_errors,
            "conflicts": 0,
            "zones_blocked": zones_blocked,
            "events_delayed": events_delayed,
        }
    finally:
        conn.close()


def render_dashboard_view(page: ft.Page, on_refresh):
    data = _fetch_context()

    def _sync_now(e):
        try:
            SyncService().run()
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Sync iniciado."),
                bgcolor=ft.Colors.GREEN_400,
                open=True,
                duration=2000,
            )
        except Exception:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Nao foi possivel iniciar o sync."),
                bgcolor=ft.Colors.RED_400,
                open=True,
                duration=2000,
            )
        page.update()
        on_refresh(None)

    info = ft.Column(
        [
            ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
            ft.Text(f"Empresa ativa: {data['company_name']}"),
            ft.Text(f"Utilizador: {data['user_email']} ({data['user_role']})"),
            ft.Text(f"Ultimo bootstrap: {data['last_bootstrap']}"),
            ft.Text(f"Ultimo Pull: {data['last_pull']}"),
            ft.Text(f"Ultimo Push: {data['last_push']}"),
            ft.Text(f"Pendencias de sincronizacao: {data['pending']}"),
            ft.ElevatedButton("Sync Now", icon=ft.Icons.SYNC, on_click=_sync_now),
        ],
        spacing=6,
    )

    alerts = ft.Column(
        [
            ft.Text("Alertas criticos", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([_status_dot(data["sync_errors"] == 0), ft.Text("Erros de sync")], spacing=8),
            ft.Row([_status_dot(data["conflicts"] == 0), ft.Text("Conflitos")], spacing=8),
            ft.Row([_status_dot(data["zones_blocked"] == 0), ft.Text("Zonas bloqueadas")], spacing=8),
            ft.Row([_status_dot(data["events_delayed"] == 0), ft.Text("Eventos em atraso")], spacing=8),
        ],
        spacing=6,
    )

    return ft.Column(
        [info, ft.Divider(), alerts],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
