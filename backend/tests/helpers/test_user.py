# backend/tests/helpers/test_user.py

from dataclasses import dataclass
from app.core.user_context import UserContext


@dataclass(frozen=True)
class FakeCurrentUser(UserContext):
    company_server_id: int
    db_user_id: int