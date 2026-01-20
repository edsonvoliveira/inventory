# backend/app/services/sync/handlers/base.py

"""
Responsibilities:
- Sync handler for base entities.
- Implement pull and push operations.
"""

# backend/app/services/sync/handlers/base.py

# classe base genérica para handlers de sync

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

from app.core.user_context import UserContext


class BaseSyncHandler(ABC):
    """
    Classe base para handlers de sincronização.

    Responsabilidades:
    - PUSH: aplicar inserts / updates / deletes vindos do cliente
    - PULL: buscar dados do servidor para o cliente
    """

    # --------
    # PUSH API
    # --------

    @abstractmethod
    def insert(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        pass

    @abstractmethod
    def update(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        pass

    # ---------------------------
    # Helpers
    # ---------------------------
    def _reject_unknown_fields(self, payload: Dict[str, Any], allowed_fields: list[str]) -> None:
        unknown = set(payload.keys()) - set(allowed_fields)
        if unknown:
            fields = ", ".join(sorted(unknown))
            raise RuntimeError(f"INVALID_FIELDS:{fields}")

    def delete(
        self,
        payload: Dict[str, Any],
        record_uuid: str,
        user: UserContext,
    ) -> None:
        """
        Delete lógico (soft delete).
        Nem todas as tabelas suportam.
        """
        raise NotImplementedError("Delete não suportado para esta tabela")

    # --------
    # PULL API
    # --------

    @abstractmethod
    def pull(
        self,
        *,
        company_id: int,
        since: datetime | None,
    ) -> List[Dict[str, Any]]:
        """
        Retorna registros alterados desde `since`.
        Usado pelo PullExecutor.
        """
        pass
