# desktop/views/settings/config_view.py

"""
Responsibilities:
- Render the config view.
- Wire UI events and interactions.
"""

import flet as ft

from desktop.core.strings import CONFIG_SUBTITLE, CONFIG_TITLE
from desktop.core.sync_service import (
    SYNC_INTERVAL_META_KEY,
    get_scheduler,
    get_sync_interval_seconds,
)
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import get_meta, set_meta
from desktop.utils.datetime_format import format_ts


def _sync_status():
    conn = get_connection()
    try:
        last_pull_at = format_ts(get_meta("last_pull_at", conn) or "n/a")
        pending = conn.execute(
            "SELECT COUNT(1) FROM outbox_local WHERE status = 'pending'"
        ).fetchone()[0]
    finally:
        conn.close()
    return last_pull_at, pending


def render_config_view(page: ft.Page, on_refresh):
    coluna = ft.Column(expand=True, spacing=10)
    coluna.controls.append(ft.Text(CONFIG_TITLE, size=24, weight=ft.FontWeight.BOLD))
    coluna.controls.append(ft.Text(CONFIG_SUBTITLE))
    last_pull_at, pending = _sync_status()
    coluna.controls.append(ft.Text(f"Sync: ultimo pull = {last_pull_at}"))
    coluna.controls.append(ft.Text(f"Outbox pendente: {pending}"))

    current_interval = get_sync_interval_seconds()
    scheduler = get_scheduler()
    active_interval = scheduler.get_interval()
    dlg_interval = ft.TextField(
        label="Intervalo de sync (segundos)",
        value=str(current_interval),
        width=260,
    )
    def _build_labels(saved_value: int, active_value: int):
        is_mismatch = saved_value != active_value
        color = ft.Colors.ORANGE_700 if is_mismatch else None
        return (
            ft.Text(f"Intervalo salvo: {saved_value}s", color=color),
            ft.Text(f"Intervalo em uso: {active_value}s", color=color),
        )

    saved_label, active_label = _build_labels(current_interval, active_interval)

    def _validate_interval() -> int | None:
        raw = (dlg_interval.value or "").strip()
        try:
            value = int(raw)
        except ValueError:
            dlg_interval.error_text = "Informe valor entre 30 e 300 segundos."
            dlg_interval.update()
            return None
        if value < 30 or value > 300:
            dlg_interval.error_text = "Informe valor entre 30 e 300 segundos."
            dlg_interval.update()
            return None
        dlg_interval.error_text = None
        dlg_interval.update()
        return value

    def _save_interval(value: int) -> None:
        set_meta(SYNC_INTERVAL_META_KEY, str(value))
        saved_label.value = f"Intervalo salvo: {value}s"
        mismatch = value != scheduler.get_interval()
        saved_label.color = ft.Colors.ORANGE_700 if mismatch else None
        active_label.color = ft.Colors.ORANGE_700 if mismatch else None
        saved_label.update()
        active_label.update()

    def _show_saved(message: str) -> None:
        page.snack_bar = ft.SnackBar(content=ft.Text(message), open=True, duration=1500)
        page.update()

    def salvar_intervalo(e):
        value = _validate_interval()
        if value is None:
            return
        _save_interval(value)
        _show_saved("Intervalo salvo.")

    def aplicar_agora(e):
        value = _validate_interval()
        if value is None:
            return
        _save_interval(value)
        scheduler.set_interval(value)
        scheduler.restart()
        active_label.value = f"Intervalo em uso: {value}s"
        saved_label.color = None
        active_label.color = None
        active_label.update()
        _show_saved("Intervalo aplicado.")

    coluna.controls.append(
        ft.Row(
            [
                dlg_interval,
                ft.ElevatedButton("Salvar", on_click=salvar_intervalo),
                ft.ElevatedButton("Aplicar agora", on_click=aplicar_agora),
            ],
            spacing=8,
        )
    )
    coluna.controls.append(saved_label)
    coluna.controls.append(active_label)
    return coluna
