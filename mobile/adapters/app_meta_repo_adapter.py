from __future__ import annotations

from typing import Optional

from app_core.ports.repositories.app_meta_repo_port import AppMetaRepoPort
from mobile.data.repositories.app_meta_repo import get_meta, set_meta


class MobileAppMetaRepoAdapter(AppMetaRepoPort):
    def get_meta(self, key: str) -> Optional[str]:
        return get_meta(key)

    def set_meta(self, key: str, value: str) -> None:
        set_meta(key, value)
