# mobile/views/settings/settings_view.py

"""
Responsibilities:
- Render the settings view.
- Provide sync interval controls.
"""

import flet as ft
from datetime import datetime

from mobile.core.sync_service import (
    SYNC_INTERVAL_META_KEY,
    get_scheduler,
    get_sync_interval_seconds,
)
from mobile.core.theme import THEME, TOUCH
from mobile.data.db.connection import get_connection
from mobile.data.repositories.app_meta_repo import get_meta, set_meta
from mobile.utils.ui import toast


def _sync_status():
    conn = get_connection()
    try:
        last_pull_at = get_meta("last_pull_at") or "n/a"
        pending = conn.execute(
            "SELECT COUNT(1) FROM outbox_local WHERE status = 'pending'"
        ).fetchone()[0]
    finally:
        conn.close()
    return last_pull_at, pending


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


def settings_content(page: ft.Page):
    text_color = THEME["text_on_dark"] if page.theme_mode == ft.ThemeMode.DARK else THEME["text_on_light"]
    last_pull_at, pending = _sync_status()
    last_pull_at = _format_ts(last_pull_at)
    current_interval = get_sync_interval_seconds()
    scheduler = get_scheduler()
    active_interval = scheduler.get_interval()

    interval_field = ft.TextField(
        label="Intervalo de sync (segundos)",
        value=str(current_interval),
        width=260,
        height=TOUCH["input_height"],
    )

    def _validate_interval() -> int | None:
        raw = (interval_field.value or "").strip()
        try:
            value = int(raw)
        except ValueError:
            interval_field.error_text = "Informe valor entre 30 e 300 segundos."
            interval_field.update()
            return None
        if value < 30 or value > 300:
            interval_field.error_text = "Informe valor entre 30 e 300 segundos."
            interval_field.update()
            return None
        interval_field.error_text = None
        interval_field.update()
        return value

    def _save_interval(value: int) -> None:
        set_meta(SYNC_INTERVAL_META_KEY, str(value))

    def salvar(e):
        value = _validate_interval()
        if value is None:
            return
        _save_interval(value)
        toast(page, "Intervalo salvo.", success=True)

    def aplicar(e):
        value = _validate_interval()
        if value is None:
            return
        _save_interval(value)
        scheduler.set_interval(value)
        scheduler.restart()
        toast(page, "Intervalo aplicado.", success=True)

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

    return ft.Column(
        [
            ft.Text("Configuracoes", size=22, color=text_color),
            ft.Text(f"Sync: ultimo pull = {last_pull_at}", size=14, color=THEME["text_secondary"]),
            ft.Text(f"Outbox pendente: {pending}", size=14, color=THEME["text_secondary"]),
            ft.Text(f"Intervalo salvo: {current_interval}s", size=14, color=THEME["text_secondary"]),
            ft.Text(f"Intervalo em uso: {active_interval}s", size=14, color=THEME["text_secondary"]),
            interval_field,
            ft.Row(
                [
                    ft.ElevatedButton("Salvar", on_click=salvar, height=TOUCH["button_height"]),
                    ft.ElevatedButton("Aplicar agora", on_click=aplicar, height=TOUCH["button_height"]),
                ],
                spacing=8,
            ),
            ft.Divider(),
            info_card,
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
