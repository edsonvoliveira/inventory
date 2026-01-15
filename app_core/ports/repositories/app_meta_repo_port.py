from __future__ import annotations

from typing import Protocol, Optional


class AppMetaRepoPort(Protocol):
    def get_meta(self, key: str) -> Optional[str]:
        ...

    def set_meta(self, key: str, value: str) -> None:
        ...
