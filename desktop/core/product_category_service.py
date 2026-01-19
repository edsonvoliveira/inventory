# desktop/core/product_category_service.py

"""
Responsibilities:
- Service layer for product category workflows.
"""

from desktop.core.result import Result
from desktop.data.repositories.product_categories_repo import ProductCategoriesRepo
from desktop.utils.validation import is_required


class ProductCategoryService:
    def list(self) -> Result[list[dict]]:
        try:
            data = ProductCategoriesRepo().get_all()
        except Exception:
            return Result(
                ok=False,
                data=[],
                message="Nao foi possivel carregar as categorias.",
                error_code="CATEGORY_LIST_ERROR",
            )
        return Result(ok=True, data=data)

    def create(self, code: str, name: str, description: str | None) -> Result[None]:
        if not is_required(code) or not is_required(name):
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        try:
            ProductCategoriesRepo().create(
                {
                    "code": code.strip(),
                    "name": name.strip(),
                    "description": (description or "").strip() or None,
                }
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel criar a categoria.",
                error_code="CATEGORY_CREATE_ERROR",
            )
        return Result(ok=True)

    def update(self, uuid: str, code: str, name: str, description: str | None) -> Result[None]:
        if not is_required(code) or not is_required(name):
            return Result(ok=False, message="Informacoes obrigatorias", error_code="VALIDATION_ERROR")
        try:
            ProductCategoriesRepo().update(
                uuid,
                {
                    "code": code.strip(),
                    "name": name.strip(),
                    "description": (description or "").strip() or None,
                },
            )
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel atualizar a categoria.",
                error_code="CATEGORY_UPDATE_ERROR",
            )
        return Result(ok=True)

    def delete(self, uuid: str) -> Result[None]:
        try:
            ProductCategoriesRepo().soft_delete(uuid)
        except Exception:
            return Result(
                ok=False,
                message="Nao foi possivel remover a categoria.",
                error_code="CATEGORY_DELETE_ERROR",
            )
        return Result(ok=True)
