# desktop/core/location_service.py

"""
Responsibilities:
- Service layer for location workflows.
"""

from desktop.core.result import Result
from desktop.data.repositories.locations_repo import LocationsRepo
from desktop.data.repository import (
    company_get_all,
    location_get_all,
)
from desktop.utils.validation import is_required


class LocationService:
    def _resolve_company_id(self) -> int | None:
        companies = company_get_all()
        if not companies:
            return None
        return int(companies[0]["id"])

    def list(self) -> Result[list[dict]]:
        try:
            return Result(ok=True, data=location_get_all())
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar os locais.",
                error_code="LOCATION_LIST_ERROR",
            )

    def create(self, name: str) -> Result[None]:
        if not is_required(name):
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        company_id = self._resolve_company_id()
        if not company_id:
            return Result(ok=False, message="Empresa nao encontrada.", error_code="COMPANY_REQUIRED")
        try:
            LocationsRepo().create(
                {
                    "code": name.strip(),
                    "name": name.strip(),
                    "address": None,
                }
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar o local.",
                error_code="LOCATION_CREATE_ERROR",
            )
        return Result(ok=True)

    def update(self, location_id: int, name: str) -> Result[None]:
        if not is_required(name):
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        company_id = self._resolve_company_id()
        if not company_id:
            return Result(ok=False, message="Empresa nao encontrada.", error_code="COMPANY_REQUIRED")
        try:
            # Map local id to uuid
            rows = location_get_all()
            location_uuid = next((r.get("uuid") for r in rows if r.get("id") == location_id), None)
            if not location_uuid:
                return Result(ok=False, message="Local nao encontrado.", error_code="LOCATION_NOT_FOUND")
            LocationsRepo().update(
                location_uuid,
                {
                    "code": name.strip(),
                    "name": name.strip(),
                    "address": None,
                },
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar o local.",
                error_code="LOCATION_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, location_id: int) -> Result[None]:
        try:
            rows = location_get_all()
            location_uuid = next((r.get("uuid") for r in rows if r.get("id") == location_id), None)
            if not location_uuid:
                return Result(ok=False, message="Local nao encontrado.", error_code="LOCATION_NOT_FOUND")
            LocationsRepo().soft_delete(location_uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover o local.",
                error_code="LOCATION_DELETE_ERROR",
            )
        return Result(ok=True)
