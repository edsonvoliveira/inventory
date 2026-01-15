# desktop/views/settings/config_view.py

"""
Responsibilities:
- Render the config view.
- Wire UI events and interactions.
"""

import flet as ft

from desktop.core.strings import CONFIG_SUBTITLE, CONFIG_TITLE
from desktop.data.db.connection import get_connection
from desktop.data.repositories.app_meta_repo import get_meta


def _sync_status():
    conn = get_connection()
    try:
        last_pull_at = get_meta("last_pull_at", conn) or "n/a"
        pending = conn.execute(
            "SELECT COUNT(1) FROM outbox_local WHERE status = 'pending'"
        ).fetchone()[0]
    finally:
        conn.close()
    return last_pull_at, pending


def render_config_view():
    coluna = ft.Column(expand=True, spacing=10)
    coluna.controls.append(ft.Text(CONFIG_TITLE, size=24, weight=ft.FontWeight.BOLD))
    coluna.controls.append(ft.Text(CONFIG_SUBTITLE))
    last_pull_at, pending = _sync_status()
    coluna.controls.append(ft.Text(f"Sync: ultimo pull = {last_pull_at}"))
    coluna.controls.append(ft.Text(f"Outbox pendente: {pending}"))
    return coluna
