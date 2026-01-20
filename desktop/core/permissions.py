from __future__ import annotations

from desktop.core.session_service import SessionService
from desktop.data.repositories.users_repo import UsersRepo


_ADMIN_ENTITIES = {
    "devices",
    "locations",
    "products",
    "product_barcodes",
    "product_categories",
    "inventory_events",
    "inventory_event_targets",
    "zones",
    "users",
}
_MANAGER_ENTITIES = _ADMIN_ENTITIES - {"users"}


def get_current_role() -> str | None:
    user_server_id = SessionService.get_user_server_id()
    if not user_server_id:
        return None
    try:
        user = UsersRepo().get_by_server_id(int(user_server_id))
    except Exception:
        return None
    if not user:
        return None
    return str(user.get("role") or "").strip() or None


def can_write_entity(entity: str) -> bool:
    role = get_current_role()
    if role == "admin":
        return entity in _ADMIN_ENTITIES and entity != "companies"
    if role == "manager":
        return entity in _MANAGER_ENTITIES
    return False
