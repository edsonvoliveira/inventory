from __future__ import annotations

from typing import Optional

from app_core.ports.repositories.app_meta_repo_port import AppMetaRepoPort
from desktop.data.repositories import app_meta_repo


class DesktopAppMetaRepoAdapter(AppMetaRepoPort):
    def get_meta(self, key: str) -> Optional[str]:
        return app_meta_repo.get_meta(key)

    def set_meta(self, key: str, value: str) -> None:
        app_meta_repo.set_meta(key, value)
