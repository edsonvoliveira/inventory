# backend/app/services/sync/base.py

# classe base genérica para handlers de sync

from abc import ABC, abstractmethod
from typing import Dict, Any

from app.core.security import CurrentUser


class BaseSyncHandler(ABC):

    @abstractmethod
    def insert(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser):
        pass

    @abstractmethod
    def update(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser):
        pass

    def delete(self, payload: Dict[str, Any], record_uuid: str, user: CurrentUser):
        raise NotImplementedError("Delete não suportado para esta tabela")
