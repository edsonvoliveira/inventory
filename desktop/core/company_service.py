# desktop/core/company_service.py

"""
Responsibilities:
- Service layer for company workflows.
"""

from desktop.core.result import Result
from desktop.data.repository import (
    company_create,
    company_delete,
    company_get,
    company_get_all,
    company_update,
)
from desktop.utils.validation import is_required


class CompanyService:
    def list(self) -> Result[list[dict]]:
        try:
            return Result(ok=True, data=company_get_all())
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar as empresas.",
                error_code="COMPANY_LIST_ERROR",
            )

    def create(self, name: str, nif: str | None) -> Result[dict | None]:
        if not is_required(name):
            return Result(ok=False, message="Nome obrigatorio.", error_code="VALIDATION_ERROR")
        try:
            company_create(name.strip(), nif)
            data = company_get_all()
            created = data[-1] if data else None
            return Result(ok=True, data=created)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar a empresa.",
                error_code="COMPANY_CREATE_ERROR",
            )

    def update(self, company_id: int, name: str, nif: str | None) -> Result[dict | None]:
        if not is_required(name):
            return Result(ok=False, message="Nome obrigatorio.", error_code="VALIDATION_ERROR")
        try:
            company_update(company_id, name.strip(), nif)
            return Result(ok=True, data=company_get(company_id))
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar a empresa.",
                error_code="COMPANY_UPDATE_ERROR",
            )

    def delete(self, company_id: int) -> Result[None]:
        try:
            company_delete(company_id)
            return Result(ok=True)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover a empresa.",
                error_code="COMPANY_DELETE_ERROR",
            )
