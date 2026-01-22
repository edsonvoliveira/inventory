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
from desktop.data.repositories.outbox_repo import OutboxRepo
from desktop.utils.datetime_format import format_ts


def _status_dot(ok: bool) -> ft.Container:
    color = ft.Colors.GREEN_400 if ok else ft.Colors.RED_400
    return ft.Container(width=10, height=10, bgcolor=color, border_radius=10)


def _parse_error_code(raw: str | None) -> str:
    if not raw:
        return "unknown"
    if ":" in raw:
        return raw.split(":", 1)[0]
    return raw


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
                WHERE server_id = ? AND is_active = 1
                """,
                (company_server_id,),
            ).fetchone()
            if row:
                company_name = row[0]

        if user_server_id is not None:
            row = conn.execute(
                """
                SELECT email, role FROM users_local
                WHERE server_id = ? AND is_active = 1
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
            LIMIT 8
            """
        ).fetchall()
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
            "last_bootstrap": format_ts(last_bootstrap),
            "last_pull": format_ts(last_pull),
            "last_push": format_ts(last_push),
            "pending": pending,
            "sync_errors": sync_errors,
            "error_rows": [
                {
                    "entity": r[0],
                    "operation": r[1],
                    "record_uuid": r[2],
                    "error_code": _parse_error_code(r[3]),
                    "error": r[3] or "",
                }
                for r in error_rows
            ],
            "conflicts": 0,
            "zones_blocked": zones_blocked,
            "events_delayed": events_delayed,
        }
    finally:
        conn.close()


def render_dashboard_view(page: ft.Page, on_refresh):
    timer_key = "dashboard_refresh_timer"
    if hasattr(ft, "Timer"):
        try:
            timer = page.session.get(timer_key)
            if timer is None:
                def _on_tick(_e):
                    if page.route == "/":
                        on_refresh(None)

                timer = ft.Timer(interval=15000, on_tick=_on_tick)
                page.session.set(timer_key, timer)
                page.overlay.append(timer)

            timer.start()
        except Exception:
            pass

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

    def _retry_errors(e):
        try:
            conn = get_connection()
            try:
                retried = OutboxRepo(conn).retry_failed()
                conn.commit()
            finally:
                conn.close()
            if retried:
                SyncService().run()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Reenvio iniciado para {retried} itens."),
                    bgcolor=ft.Colors.GREEN_400,
                    open=True,
                    duration=2500,
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Nao ha itens para reenvio."),
                    bgcolor=ft.Colors.BLUE_400,
                    open=True,
                    duration=2000,
                )
        except Exception:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Nao foi possivel reenviar os itens."),
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
            ft.Row(
                [
                    ft.ElevatedButton("Sync Now", icon=ft.Icons.SYNC, on_click=_sync_now),
                    ft.OutlinedButton("Retry erros", icon=ft.Icons.REFRESH, on_click=_retry_errors),
                ],
                spacing=8,
            ),
        ],
        spacing=6,
    )

    error_rows = data.get("error_rows", [])
    error_list = (
        ft.Column(
            [
                ft.Text(
                    f"{row['entity']} {row['operation']} ({row['record_uuid']}) - {row['error_code']}",
                    size=12,
                )
                for row in error_rows
            ],
            spacing=4,
        )
        if error_rows
        else ft.Text("Sem erros recentes.")
    )

    alerts = ft.Column(
        [
            ft.Text("Alertas criticos", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([_status_dot(data["sync_errors"] == 0), ft.Text("Erros de sync")], spacing=8),
            ft.Row([_status_dot(data["conflicts"] == 0), ft.Text("Conflitos")], spacing=8),
            ft.Row([_status_dot(data["zones_blocked"] == 0), ft.Text("Zonas bloqueadas")], spacing=8),
            ft.Row([_status_dot(data["events_delayed"] == 0), ft.Text("Eventos em atraso")], spacing=8),
            ft.Text("Erros recentes (entidade/operacao/codigo)", size=12, weight=ft.FontWeight.BOLD),
            error_list,
        ],
        spacing=6,
    )

    return ft.Column(
        [info, ft.Divider(), alerts],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
